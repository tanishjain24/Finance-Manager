from app import db, login
from datetime import datetime, timedelta
from time import time as epoch_time
import jwt
import secrets
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(UserMixin, db.Model):
	user_id		= db.Column(db.Integer, primary_key=True)
	first_name 	= db.Column(db.String(32), index=True)
	last_name 	= db.Column(db.String(32), index=True)
	email 		= db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	last_seen 	= db.Column(db.DateTime, default=datetime.utcnow)
	networth 	= db.Column(db.Numeric(scale=2), nullable=True, default=0)
	email_verified = db.Column(db.Boolean, default=False)
	verification_token = db.Column(db.String(128), nullable=True, default=None)

	accounts = db.relationship('Account', backref='owner', \
		cascade='all, delete-orphan', lazy='dynamic')
	transaction_history = db.relationship('Transaction', backref='owner', \
	 	cascade='all, delete-orphan', lazy='dynamic')
	categories = db.relationship('Category', backref='owner', \
	 	cascade='all, delete-orphan', lazy='dynamic')
	settings = db.relationship('UserSettings', backref='user', uselist=False, \
		cascade='all, delete-orphan')
	budgets = db.relationship('Budget', backref='owner', \
		cascade='all, delete-orphan', lazy='dynamic')
	savings_goals = db.relationship('SavingsGoal', backref='owner', \
		cascade='all, delete-orphan', lazy='dynamic')
	bills = db.relationship('BillReminder', backref='owner', \
		cascade='all, delete-orphan', lazy='dynamic')

	def __repr__(self):
		return '<User {} {} {}>'.format(self.user_id, self.first_name, self.last_name)

	def get_id(self):
		return self.user_id

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_password_reset_token(self, valid_duration=1800):
		exp_time = epoch_time() + valid_duration
		return jwt.encode(
			{
				'reset_password': self.user_id,
				'exp': exp_time
			}, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	def get_email_verification_token(self, valid_duration=86400):
		exp_time = epoch_time() + valid_duration
		return jwt.encode(
			{
				'verify_email': self.user_id,
				'exp': exp_time
			}, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	def generate_verification_token(self):
		self.verification_token = secrets.token_urlsafe(32)
		return self.verification_token

	def get_networth(self):
		networth = 0
		for account in self.accounts.all():
			networth = networth + account.account_networth
		return networth

	def get_settings(self):
		if not self.settings:
			settings = UserSettings(user_id=self.user_id)
			db.session.add(settings)
			db.session.commit()
		return self.settings

	@staticmethod
	def verify_password_reset_token(token):
		try:
			user_id = jwt.decode(token , current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(user_id)

	@staticmethod
	def verify_email_token(token):
		try:
			user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['verify_email']
		except:
			return
		return User.query.get(user_id)


class UserSettings(db.Model):
	settings_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), unique=True)
	currency = db.Column(db.String(3), default='USD')
	theme = db.Column(db.String(10), default='dark')
	notifications_enabled = db.Column(db.Boolean, default=True)
	email_notifications = db.Column(db.Boolean, default=True)

	def __repr__(self):
		return '<UserSettings user={}>'.format(self.user_id)


class Account(db.Model):
	ACCOUNT_TYPES = ['bank', 'wallet', 'credit_card', 'cash', 'investment']

	account_id		= db.Column(db.Integer, primary_key=True)
	user_id			= db.Column(db.Integer, db.ForeignKey('user.user_id'))
	account_name 	= db.Column(db.String(64))
	account_networth = db.Column(db.Numeric(scale=2), nullable=True, default=0)
	date_added 		= db.Column(db.DateTime, default=datetime.utcnow)
	date_modified 	= db.Column(db.DateTime, default=datetime.utcnow)
	institution 	= db.Column(db.String(64), nullable=True, default=None)
	account_type 	= db.Column(db.String(20), default='bank')

	transaction_history = db.relationship('Transaction', backref='account', \
	 	cascade='all, delete-orphan', lazy='dynamic')

	def __repr__(self):
		if self.institution:
			return '<Account {} {}>'.format(self.institution, self.account_name)
		return '<Account {}>'.format(self.account_name)

	def display_name(self):
		if self.institution:
			return '{} - {}'.format(self.institution, self.account_name)
		return self.account_name

	def type_icon(self):
		icons = {
			'bank': '🏦', 'wallet': '👛', 'credit_card': '💳',
			'cash': '💵', 'investment': '📈',
		}
		return icons.get(self.account_type, '🏦')


class Transaction(db.Model):
	transaction_id	= db.Column(db.Integer, primary_key=True)
	user_id			= db.Column(db.Integer, db.ForeignKey('user.user_id'))
	account_id		= db.Column(db.Integer, db.ForeignKey('account.account_id'))
	category_id 	= db.Column(db.Integer, db.ForeignKey('category.category_id'))
	transaction_name = db.Column(db.String(40))
	amount			= db.Column(db.Numeric(scale=2))
	timestamp		= db.Column(db.DateTime, default=datetime.utcnow)
	recurring		= db.Column(db.Boolean, default=False)
	recurring_delay = db.Column(db.Interval, nullable=True, default=None)
	recurring_enddate = db.Column(db.DateTime, nullable=True, default=None)
	note 			= db.Column(db.String(120), nullable=True, default=None)
	delete_allowed	= db.Column(db.Boolean, default=True)

	def __repr__(self):
		return '<Transaction {} {}>'.format(self.transaction_name, self.amount)

	def is_income(self):
		return float(self.amount) > 0

	def is_expense(self):
		return float(self.amount) < 0

	@staticmethod
	def set_recurring_delay(how_often):
		if how_often == 'Weekly':
			return timedelta(weeks=1)
		elif how_often == 'Monthly':
			return timedelta(days=30)
		elif how_often == 'Yearly':
			return timedelta(days=365)

	@staticmethod
	def set_recurring_enddate(date):
		t = datetime.min.time()
		return datetime.combine(date, t)


class Category(db.Model):
	category_id 		= db.Column(db.Integer, primary_key=True)
	user_id 			= db.Column(db.Integer, db.ForeignKey('user.user_id'))
	parent_category_id	= db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=True, default=None)
	category_name 		= db.Column(db.String(40))
	user_deleted 		= db.Column(db.Boolean, default=False)

	transactions = db.relationship('Transaction', backref='category', lazy='dynamic')

	def __repr__(self):
		return '<Category {}>'.format(self.category_name)

	@staticmethod
	def load_initial_categories():
		return ["Rent", "Restaurants", "Groceries", "Auto", "Miscellaneous", \
			"Loan", "Clothing", "Hobbies", "Sporting Goods", "Books", "Electronics", \
			"Charity", "Gift", "Medical", "Home Improvement", "Kids", "Salary", "Freelance"]


class Budget(db.Model):
	budget_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
	amount = db.Column(db.Numeric(scale=2))
	month = db.Column(db.Integer)
	year = db.Column(db.Integer)

	category = db.relationship('Category', backref='budgets')

	def __repr__(self):
		return '<Budget {} {}/{}>'.format(self.category_id, self.month, self.year)

	def spent(self):
		from sqlalchemy import extract, and_
		total = db.session.query(db.func.sum(Transaction.amount)).filter(
			Transaction.user_id == self.user_id,
			Transaction.category_id == self.category_id,
			extract('month', Transaction.timestamp) == self.month,
			extract('year', Transaction.timestamp) == self.year,
			Transaction.amount < 0,
		).scalar()
		return abs(float(total or 0))

	def progress_percent(self):
		if float(self.amount) == 0:
			return 0
		return min(100, round(self.spent() / float(self.amount) * 100, 1))

	def is_over_budget(self):
		return self.spent() > float(self.amount)


class SavingsGoal(db.Model):
	goal_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	name = db.Column(db.String(64))
	target_amount = db.Column(db.Numeric(scale=2))
	current_amount = db.Column(db.Numeric(scale=2), default=0)
	deadline = db.Column(db.DateTime, nullable=True)
	icon = db.Column(db.String(10), default='🎯')
	color = db.Column(db.String(20), default='emerald')
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<SavingsGoal {}>'.format(self.name)

	def progress_percent(self):
		if float(self.target_amount) == 0:
			return 0
		return min(100, round(float(self.current_amount) / float(self.target_amount) * 100, 1))


class BillReminder(db.Model):
	bill_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
	name = db.Column(db.String(64))
	amount = db.Column(db.Numeric(scale=2))
	due_date = db.Column(db.DateTime)
	recurring = db.Column(db.Boolean, default=False)
	recurring_interval = db.Column(db.String(20), nullable=True)
	is_paid = db.Column(db.Boolean, default=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<BillReminder {}>'.format(self.name)

	def is_overdue(self):
		return not self.is_paid and self.due_date < datetime.utcnow()

	def days_until_due(self):
		delta = self.due_date - datetime.utcnow()
		return delta.days
