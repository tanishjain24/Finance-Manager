"""Dashboard and analytics helper functions."""
from datetime import datetime
from sqlalchemy import extract, func
from app.models import Transaction, Category, Budget, BillReminder


def get_user_settings(user):
	return user.get_settings()


def format_money(amount, currency='USD'):
	symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹', 'JPY': '¥'}
	symbol = symbols.get(currency, '$')
	val = float(amount or 0)
	if val < 0:
		return '-{}{:,.2f}'.format(symbol, abs(val))
	return '{}{:,.2f}'.format(symbol, val)


def get_dashboard_stats(user):
	now = datetime.utcnow()
	month, year = now.month, now.year
	settings = user.get_settings()
	currency = settings.currency

	total_balance = float(user.get_networth())
	monthly_income = db_sum(user, month, year, positive=True)
	monthly_expenses = abs(db_sum(user, month, year, positive=False))
	savings = monthly_income - monthly_expenses

	overdue_bills = BillReminder.query.filter(
		BillReminder.user_id == user.user_id,
		BillReminder.is_paid == False,
		BillReminder.due_date < now,
	).count()

	over_budget_count = sum(
		1 for b in user.budgets.filter(Budget.month == month, Budget.year == year).all()
		if b.is_over_budget()
	)

	return {
		'total_balance': total_balance,
		'monthly_income': monthly_income,
		'monthly_expenses': monthly_expenses,
		'savings': savings,
		'net_worth': total_balance,
		'accounts_count': user.accounts.count(),
		'transactions_count': user.transaction_history.count(),
		'overdue_bills': overdue_bills,
		'over_budget_count': over_budget_count,
		'currency': currency,
		'month': month,
		'year': year,
	}


def db_sum(user, month, year, positive=True):
	from app import db
	q = db.session.query(func.sum(Transaction.amount)).filter(
		Transaction.user_id == user.user_id,
		extract('month', Transaction.timestamp) == month,
		extract('year', Transaction.timestamp) == year,
	)
	if positive:
		q = q.filter(Transaction.amount > 0)
	else:
		q = q.filter(Transaction.amount < 0)
	return float(q.scalar() or 0)


def get_monthly_trend(user, months=6):
	now = datetime.utcnow()
	labels, income_data, expense_data = [], [], []
	for i in range(months - 1, -1, -1):
		m = now.month - i
		y = now.year
		while m <= 0:
			m += 12
			y -= 1
		label = datetime(y, m, 1).strftime('%b %Y')
		labels.append(label)
		income_data.append(db_sum(user, m, y, positive=True))
		expense_data.append(abs(db_sum(user, m, y, positive=False)))
	return labels, income_data, expense_data


def get_category_breakdown(user, month=None, year=None):
	from app import db
	now = datetime.utcnow()
	month = month or now.month
	year = year or now.year
	results = db.session.query(
		Category.category_name,
		func.sum(Transaction.amount),
	).join(Transaction, Transaction.category_id == Category.category_id).filter(
		Transaction.user_id == user.user_id,
		Transaction.amount < 0,
		extract('month', Transaction.timestamp) == month,
		extract('year', Transaction.timestamp) == year,
	).group_by(Category.category_name).all()

	return [r[0] for r in results], [abs(float(r[1])) for r in results]


def get_income_vs_expense(user, month=None, year=None):
	now = datetime.utcnow()
	month = month or now.month
	year = year or now.year
	return db_sum(user, month, year, positive=True), abs(db_sum(user, month, year, positive=False))


def build_transaction_array(account=None, user=None, limit=None):
	from app.models import Account as Acct, Category as Cat
	transaction_array = []
	if user:
		query = user.transaction_history.order_by(Transaction.timestamp.desc())
		if limit:
			query = query.limit(limit)
		for transaction in query.all():
			category = Cat.query.get(transaction.category_id)
			acct = Acct.query.get(transaction.account_id)
			transaction_array.append({
				't': transaction,
				'account_name': acct.display_name() if acct else 'Unknown',
				'category_name': category.category_name if category else 'Uncategorized',
			})
		return transaction_array

	if account:
		for transaction in account.transaction_history.order_by(Transaction.timestamp.desc()).all():
			category = Cat.query.get(transaction.category_id)
			transaction_array.append({
				't': transaction,
				'category_name': category.category_name if category else 'Uncategorized',
			})
		return transaction_array


def get_category_icon(name):
	icons = {
		'Rent': '🏠', 'Restaurants': '🍽️', 'Groceries': '🛒', 'Auto': '🚗',
		'Miscellaneous': '📦', 'Loan': '🏦', 'Clothing': '👕', 'Hobbies': '🎨',
		'Sporting Goods': '⚽', 'Books': '📚', 'Electronics': '💻', 'Charity': '❤️',
		'Gift': '🎁', 'Medical': '🏥', 'Home Improvement': '🔧', 'Kids': '👶',
		'Salary': '💰', 'Freelance': '💼',
	}
	return icons.get(name, '📌')
