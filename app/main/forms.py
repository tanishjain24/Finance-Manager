from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, PasswordField, BooleanField, DateField, \
	SubmitField, DecimalField, RadioField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange


class DeleteProfileForm(FlaskForm):
	delete = SubmitField('Delete Profile')


class AddAccountForm(FlaskForm):
	account_name = StringField('Account Name', validators=[DataRequired()])
	institution = StringField('Institution (Optional)')
	account_type = SelectField('Account Type', choices=[
		('bank', 'Bank Account'), ('wallet', 'Wallet'),
		('credit_card', 'Credit Card'), ('cash', 'Cash'),
		('investment', 'Investment'),
	], default='bank')
	account_networth = DecimalField('Opening Balance', places=2, default=0)
	submit = SubmitField('Add Account')


class EditAccountForm(FlaskForm):
	account_name = StringField('Account Name', validators=[DataRequired()])
	institution = StringField('Institution (Optional)')
	account_type = SelectField('Account Type', choices=[
		('bank', 'Bank Account'), ('wallet', 'Wallet'),
		('credit_card', 'Credit Card'), ('cash', 'Cash'),
		('investment', 'Investment'),
	])
	submit = SubmitField('Save Changes')


class AddTransactionForm(FlaskForm):
	transaction_name = StringField('Transaction Name', validators=[DataRequired()])
	transaction_type = RadioField('Transaction Type', \
		choices=[('Income','Income'), ('Expense','Expense')], default='Expense')
	category = SelectField('Category:', choices=[], coerce=int)
	amount = DecimalField('Amount', places=2, validators=[DataRequired()])
	recurring = RadioField('One-Time Transaction?', \
		choices=[('False','Yes'), ('True','No')], default='False')
	how_often = SelectField('Repeats:', \
		choices=[('Weekly','Weekly'), ('Monthly','Monthly'), ('Yearly','Yearly')])
	enddate = DateField('Recurring End (YYYY-MM-DD)', default=datetime.utcnow)
	note = StringField('Notes (Optional)')
	submit = SubmitField('Submit Transaction')


class EditTransactionForm(FlaskForm):
	transaction_name = StringField('Transaction Name', validators=[DataRequired()])
	transaction_type = RadioField('Transaction Type', \
		choices=[('Income','Income'), ('Expense','Expense')])
	category = SelectField('Category:', choices=[], coerce=int)
	amount = DecimalField('Amount', places=2, validators=[DataRequired()])
	note = StringField('Notes (Optional)')
	submit = SubmitField('Save Changes')


class TransactionFilterForm(FlaskForm):
	search = StringField('Search', validators=[Optional()])
	category = SelectField('Category', coerce=int, validators=[Optional()])
	transaction_type = SelectField('Type', choices=[
		('', 'All'), ('income', 'Income'), ('expense', 'Expense'),
	])
	date_from = DateField('From', validators=[Optional()])
	date_to = DateField('To', validators=[Optional()])
	submit = SubmitField('Filter')


class BudgetForm(FlaskForm):
	category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()])
	amount = DecimalField('Budget Amount', places=2, validators=[DataRequired()])
	month = IntegerField('Month', validators=[DataRequired(), NumberRange(1, 12)], default=datetime.utcnow().month)
	year = IntegerField('Year', validators=[DataRequired()], default=datetime.utcnow().year)
	submit = SubmitField('Set Budget')


class SavingsGoalForm(FlaskForm):
	name = StringField('Goal Name', validators=[DataRequired()])
	target_amount = DecimalField('Target Amount', places=2, validators=[DataRequired()])
	current_amount = DecimalField('Current Amount', places=2, default=0)
	deadline = DateField('Deadline (Optional)', validators=[Optional()])
	icon = SelectField('Icon', choices=[
		('🎯', 'Target'), ('🏠', 'House'), ('🚗', 'Car'), ('✈️', 'Travel'),
		('🎓', 'Education'), ('💍', 'Wedding'), ('🐷', 'Savings'), ('💻', 'Tech'),
	])
	submit = SubmitField('Create Goal')


class ContributeGoalForm(FlaskForm):
	amount = DecimalField('Contribution Amount', places=2, validators=[DataRequired()])
	submit = SubmitField('Add Contribution')


class BillForm(FlaskForm):
	name = StringField('Bill Name', validators=[DataRequired()])
	amount = DecimalField('Amount', places=2, validators=[DataRequired()])
	due_date = DateField('Due Date', validators=[DataRequired()])
	recurring = BooleanField('Recurring Bill')
	recurring_interval = SelectField('Repeat', choices=[
		('monthly', 'Monthly'), ('weekly', 'Weekly'), ('yearly', 'Yearly'),
	], default='monthly')
	submit = SubmitField('Add Bill')
