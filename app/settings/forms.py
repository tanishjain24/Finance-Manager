from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional


class ProfileForm(FlaskForm):
	first_name = StringField('First Name', validators=[DataRequired(), Length(max=32)])
	last_name = StringField('Last Name', validators=[DataRequired(), Length(max=32)])
	email = StringField('Email', validators=[DataRequired(), Length(max=120)])
	submit = SubmitField('Save Profile')


class ChangePasswordForm(FlaskForm):
	current_password = PasswordField('Current Password', validators=[DataRequired()])
	password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
	password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Change Password')


class PreferencesForm(FlaskForm):
	currency = SelectField('Currency', choices=[
		('USD', 'USD — US Dollar'),
		('EUR', 'EUR — Euro'),
		('GBP', 'GBP — British Pound'),
		('INR', 'INR — Indian Rupee'),
		('JPY', 'JPY — Japanese Yen'),
	])
	theme = SelectField('Theme', choices=[
		('dark', 'Dark'), ('light', 'Light'), ('system', 'System'),
	])
	notifications_enabled = BooleanField('Enable Notifications')
	email_notifications = BooleanField('Email Notifications')
	submit = SubmitField('Save Preferences')
