from app import db
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from sqlalchemy import extract, or_
from app.main import bp
from app.main.forms import *
from app.models import User, Account, Transaction, Category, Budget, SavingsGoal, BillReminder
from app.services.dashboard import (
	get_dashboard_stats, format_money, build_transaction_array,
	get_monthly_trend, get_category_breakdown, get_income_vs_expense,
	get_category_icon,
)
from app.services.export import export_transactions_csv, export_transactions_excel, export_transactions_pdf
import decimal

PER_PAGE = 15


@bp.before_app_request
def before_request():
	if current_user.is_authenticated:
		from flask import session
		session.permanent = True
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@bp.context_processor
def inject_globals():
	if current_user.is_authenticated:
		settings = current_user.get_settings()
		return {
			'user_settings': settings,
			'fmt': lambda amt: format_money(amt, settings.currency),
		}
	return {'user_settings': None, 'fmt': lambda amt: format_money(amt)}


def build_user_category_array(user, include_all=False):
	categories = user.categories.filter_by(user_deleted=False).order_by(Category.category_name).all()
	choices = []
	if include_all:
		choices.append((0, 'All Categories'))
	for category in categories:
		choices.append((category.category_id, category.category_name))
	return choices


# ── Dashboard ──────────────────────────────────────────────────────────

@bp.route('/')
@bp.route('/index')
@login_required
def index():
	return redirect(url_for('main.dashboard'))


@bp.route('/dashboard')
@login_required
def dashboard():
	current_user.networth = current_user.get_networth()
	db.session.commit()
	stats = get_dashboard_stats(current_user)
	transactions = build_transaction_array(user=current_user, limit=8)
	labels, income_data, expense_data = get_monthly_trend(current_user)
	cat_labels, cat_data = get_category_breakdown(current_user)
	accounts = current_user.accounts.limit(4).all()
	upcoming_bills = BillReminder.query.filter_by(
		user_id=current_user.user_id, is_paid=False,
	).order_by(BillReminder.due_date).limit(3).all()
	return render_template('main/dashboard.html',
		stats=stats, transactions=transactions,
		chart_labels=labels, income_data=income_data, expense_data=expense_data,
		cat_labels=cat_labels, cat_data=cat_data,
		accounts=accounts, upcoming_bills=upcoming_bills,
		get_category_icon=get_category_icon,
	)


@bp.route('/profile')
@login_required
def profile():
	return redirect(url_for('main.dashboard'))


# ── Accounts ───────────────────────────────────────────────────────────

@bp.route('/accounts')
@login_required
def accounts():
	accts = current_user.accounts.all()
	total = sum(float(a.account_networth) for a in accts)
	return render_template('main/accounts.html', accounts=accts, total=total)


@bp.route('/add_account', methods=['GET', 'POST'])
@login_required
def add_account():
	form = AddAccountForm()
	if form.validate_on_submit():
		for account in current_user.accounts.all():
			if account.account_name == form.account_name.data:
				flash('Account name already exists.', 'error')
				return render_template('main/add_account.html', form=form)
		new_account = Account(
			account_name=form.account_name.data,
			user_id=current_user.user_id,
			institution=form.institution.data,
			account_type=form.account_type.data,
			account_networth=form.account_networth.data or 0,
		)
		db.session.add(new_account)
		db.session.commit()
		flash('Account {} added successfully.'.format(new_account.account_name), 'success')
		return redirect(url_for('main.accounts'))
	return render_template('main/add_account.html', form=form)


@bp.route('/account/<account_id>')
@login_required
def account(account_id):
	acct = Account.query.get_or_404(account_id)
	if acct.user_id != current_user.user_id:
		abort(403)
	transactions = build_transaction_array(account=acct)
	return render_template('main/account.html', account=acct, transactions=transactions)


@bp.route('/account/<account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
	acct = Account.query.get_or_404(account_id)
	if acct.user_id != current_user.user_id:
		abort(403)
	form = EditAccountForm(
		account_name=acct.account_name,
		institution=acct.institution,
		account_type=acct.account_type,
	)
	if form.validate_on_submit():
		acct.account_name = form.account_name.data
		acct.institution = form.institution.data
		acct.account_type = form.account_type.data
		acct.date_modified = datetime.utcnow()
		db.session.commit()
		flash('Account updated.', 'success')
		return redirect(url_for('main.account', account_id=account_id))
	return render_template('main/edit_account.html', form=form, account=acct)


@bp.route('/delete_account/<account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
	acct = Account.query.get_or_404(account_id)
	if acct.user_id != current_user.user_id:
		abort(403)
	db.session.delete(acct)
	db.session.commit()
	flash('Account deleted.', 'success')
	return redirect(url_for('main.accounts'))


@bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
	name = current_user.first_name + ' ' + current_user.last_name
	db.session.delete(current_user)
	db.session.commit()
	flash('User {} successfully deleted'.format(name))
	return redirect(url_for('auth.login'))


# ── Transactions ───────────────────────────────────────────────────────

@bp.route('/transactions')
@login_required
def transactions():
	page = request.args.get('page', 1, type=int)
	search = request.args.get('search', '')
	category_id = request.args.get('category', 0, type=int)
	tx_type = request.args.get('type', '')

	query = current_user.transaction_history
	if search:
		query = query.filter(or_(
			Transaction.transaction_name.ilike('%{}%'.format(search)),
			Transaction.note.ilike('%{}%'.format(search)),
		))
	if category_id:
		query = query.filter(Transaction.category_id == category_id)
	if tx_type == 'income':
		query = query.filter(Transaction.amount > 0)
	elif tx_type == 'expense':
		query = query.filter(Transaction.amount < 0)

	pagination = query.order_by(Transaction.timestamp.desc()).paginate(
		page=page, per_page=PER_PAGE, error_out=False,
	)
	items = []
	for t in pagination.items:
		cat = Category.query.get(t.category_id)
		acct = Account.query.get(t.account_id)
		items.append({
			't': t,
			'category_name': cat.category_name if cat else 'Uncategorized',
			'account_name': acct.display_name() if acct else 'Unknown',
		})

	filter_form = TransactionFilterForm()
	filter_form.category.choices = build_user_category_array(current_user, include_all=True)

	return render_template('main/transactions.html',
		transactions=items, pagination=pagination,
		filter_form=filter_form, search=search,
		category_id=category_id, tx_type=tx_type,
		get_category_icon=get_category_icon,
	)


@bp.route('/add_transaction/<account_id>', methods=['GET', 'POST'])
@login_required
def add_transaction(account_id):
	acct = Account.query.get_or_404(account_id)
	if acct.user_id != current_user.user_id:
		abort(403)
	form = AddTransactionForm()
	form.category.choices = build_user_category_array(current_user)

	if form.validate_on_submit():
		if form.transaction_type.data == 'Expense':
			amount = decimal.Decimal(0.00) - form.amount.data
		else:
			amount = form.amount.data

		tr = Transaction(
			transaction_name=form.transaction_name.data,
			user_id=current_user.user_id, account_id=account_id,
			amount=amount, note=form.note.data,
			category_id=int(form.category.data),
		)
		if form.recurring.data == 'True':
			tr.recurring = True
			tr.recurring_delay = Transaction.set_recurring_delay(form.how_often.data)
			tr.recurring_enddate = Transaction.set_recurring_enddate(form.enddate.data)

		acct.account_networth += amount
		db.session.add(tr)
		db.session.commit()
		flash('Transaction added successfully.', 'success')
		return redirect(url_for('main.account', account_id=account_id))

	return render_template('main/add_transaction.html', form=form, account=acct)


@bp.route('/transaction/<transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
	tr = Transaction.query.get_or_404(transaction_id)
	if tr.user_id != current_user.user_id:
		abort(403)
	acct = Account.query.get(tr.account_id)
	form = EditTransactionForm()
	form.category.choices = build_user_category_array(current_user)

	if request.method == 'GET':
		form.transaction_name.data = tr.transaction_name
		form.category.data = tr.category_id
		form.note.data = tr.note
		form.transaction_type.data = 'Income' if float(tr.amount) > 0 else 'Expense'
		form.amount.data = abs(tr.amount)

	if form.validate_on_submit():
		old_amount = tr.amount
		if form.transaction_type.data == 'Expense':
			new_amount = decimal.Decimal(0.00) - form.amount.data
		else:
			new_amount = form.amount.data

		tr.transaction_name = form.transaction_name.data
		tr.category_id = int(form.category.data)
		tr.note = form.note.data
		tr.amount = new_amount
		acct.account_networth += (new_amount - old_amount)
		db.session.commit()
		flash('Transaction updated.', 'success')
		return redirect(url_for('main.transactions'))

	return render_template('main/edit_transaction.html', form=form, transaction=tr)


@bp.route('/transaction/<transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
	tr = Transaction.query.get_or_404(transaction_id)
	if tr.user_id != current_user.user_id or not tr.delete_allowed:
		abort(403)
	acct = Account.query.get(tr.account_id)
	acct.account_networth -= tr.amount
	db.session.delete(tr)
	db.session.commit()
	flash('Transaction deleted.', 'success')
	return redirect(request.referrer or url_for('main.transactions'))


# ── Analytics ──────────────────────────────────────────────────────────

@bp.route('/analytics')
@login_required
def analytics():
	month = request.args.get('month', datetime.utcnow().month, type=int)
	year = request.args.get('year', datetime.utcnow().year, type=int)
	cat_labels, cat_data = get_category_breakdown(current_user, month, year)
	labels, income_data, expense_data = get_monthly_trend(current_user, 12)
	income, expenses = get_income_vs_expense(current_user, month, year)
	return render_template('main/analytics.html',
		cat_labels=cat_labels, cat_data=cat_data,
		chart_labels=labels, income_data=income_data, expense_data=expense_data,
		month=month, year=year, income=income, expenses=expenses,
		net=income - expenses,
	)


# ── Budget ─────────────────────────────────────────────────────────────

@bp.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
	now = datetime.utcnow()
	form = BudgetForm()
	form.category.choices = build_user_category_array(current_user)

	if form.validate_on_submit():
		existing = Budget.query.filter_by(
			user_id=current_user.user_id,
			category_id=form.category.data,
			month=form.month.data, year=form.year.data,
		).first()
		if existing:
			existing.amount = form.amount.data
		else:
			b = Budget(
				user_id=current_user.user_id,
				category_id=form.category.data,
				amount=form.amount.data,
				month=form.month.data, year=form.year.data,
			)
			db.session.add(b)
		db.session.commit()
		flash('Budget saved.', 'success')
		return redirect(url_for('main.budget'))

	budgets = current_user.budgets.filter(
		Budget.month == now.month, Budget.year == now.year,
	).all()
	return render_template('main/budget.html', budgets=budgets, form=form, now=now)


@bp.route('/budget/<budget_id>/delete', methods=['POST'])
@login_required
def delete_budget(budget_id):
	b = Budget.query.get_or_404(budget_id)
	if b.user_id != current_user.user_id:
		abort(403)
	db.session.delete(b)
	db.session.commit()
	flash('Budget removed.', 'success')
	return redirect(url_for('main.budget'))


# ── Savings Goals ──────────────────────────────────────────────────────

@bp.route('/savings', methods=['GET', 'POST'])
@login_required
def savings():
	form = SavingsGoalForm()
	if form.validate_on_submit():
		deadline = None
		if form.deadline.data:
			deadline = datetime.combine(form.deadline.data, datetime.min.time())
		goal = SavingsGoal(
			user_id=current_user.user_id,
			name=form.name.data,
			target_amount=form.target_amount.data,
			current_amount=form.current_amount.data or 0,
			deadline=deadline,
			icon=form.icon.data,
		)
		db.session.add(goal)
		db.session.commit()
		flash('Savings goal created!', 'success')
		return redirect(url_for('main.savings'))

	goals = current_user.savings_goals.order_by(SavingsGoal.created_at.desc()).all()
	return render_template('main/savings.html', goals=goals, form=form)


@bp.route('/savings/<goal_id>/contribute', methods=['POST'])
@login_required
def contribute_goal(goal_id):
	goal = SavingsGoal.query.get_or_404(goal_id)
	if goal.user_id != current_user.user_id:
		abort(403)
	amount = request.form.get('amount', type=float)
	if amount and amount > 0:
		goal.current_amount = float(goal.current_amount) + amount
		db.session.commit()
		flash('Contribution added!', 'success')
	return redirect(url_for('main.savings'))


@bp.route('/savings/<goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
	goal = SavingsGoal.query.get_or_404(goal_id)
	if goal.user_id != current_user.user_id:
		abort(403)
	db.session.delete(goal)
	db.session.commit()
	flash('Goal deleted.', 'success')
	return redirect(url_for('main.savings'))


# ── Bills ──────────────────────────────────────────────────────────────

@bp.route('/bills', methods=['GET', 'POST'])
@login_required
def bills():
	form = BillForm()
	if form.validate_on_submit():
		bill = BillReminder(
			user_id=current_user.user_id,
			name=form.name.data,
			amount=form.amount.data,
			due_date=datetime.combine(form.due_date.data, datetime.min.time()),
			recurring=form.recurring.data,
			recurring_interval=form.recurring_interval.data if form.recurring.data else None,
		)
		db.session.add(bill)
		db.session.commit()
		flash('Bill reminder added.', 'success')
		return redirect(url_for('main.bills'))

	all_bills = current_user.bills.order_by(BillReminder.due_date).all()
	return render_template('main/bills.html', bills=all_bills, form=form)


@bp.route('/bills/<bill_id>/pay', methods=['POST'])
@login_required
def pay_bill(bill_id):
	bill = BillReminder.query.get_or_404(bill_id)
	if bill.user_id != current_user.user_id:
		abort(403)
	bill.is_paid = True
	if bill.recurring:
		from dateutil.relativedelta import relativedelta
		delta_map = {'monthly': relativedelta(months=1), 'weekly': timedelta(weeks=1), 'yearly': relativedelta(years=1)}
		delta = delta_map.get(bill.recurring_interval, relativedelta(months=1))
		new_bill = BillReminder(
			user_id=current_user.user_id,
			name=bill.name, amount=bill.amount,
			due_date=bill.due_date + delta,
			recurring=True, recurring_interval=bill.recurring_interval,
		)
		db.session.add(new_bill)
	db.session.commit()
	flash('Bill marked as paid.', 'success')
	return redirect(url_for('main.bills'))


@bp.route('/bills/<bill_id>/delete', methods=['POST'])
@login_required
def delete_bill(bill_id):
	bill = BillReminder.query.get_or_404(bill_id)
	if bill.user_id != current_user.user_id:
		abort(403)
	db.session.delete(bill)
	db.session.commit()
	flash('Bill removed.', 'success')
	return redirect(url_for('main.bills'))


# ── Reports ────────────────────────────────────────────────────────────

@bp.route('/reports')
@login_required
def reports():
	transactions = build_transaction_array(user=current_user)
	stats = get_dashboard_stats(current_user)
	return render_template('main/reports.html', transaction_count=len(transactions), stats=stats)


@bp.route('/reports/export/<fmt>')
@login_required
def export_report(fmt):
	transactions = build_transaction_array(user=current_user)
	filename = 'finance_report_{}'.format(datetime.utcnow().strftime('%Y%m%d'))
	if fmt == 'csv':
		return export_transactions_csv(transactions, filename)
	elif fmt == 'excel':
		return export_transactions_excel(transactions, filename)
	elif fmt == 'pdf':
		return export_transactions_pdf(transactions, current_user, filename)
	abort(404)


# ── AI Insights (placeholder) ──────────────────────────────────────────

@bp.route('/insights')
@login_required
def insights():
	stats = get_dashboard_stats(current_user)
	cat_labels, cat_data = get_category_breakdown(current_user)
	top_category = cat_labels[cat_data.index(max(cat_data))] if cat_data else 'N/A'
	return render_template('main/insights.html', stats=stats, top_category=top_category)
