from app import db
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Category, UserSettings
from app.auth import bp
from app.auth.forms import *
from app.auth.email import send_password_request_email, send_verification_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))
	form = LoginForm()

	next_page = request.args.get('next')
	if not next_page or url_parse(next_page).netloc != '':
		next_page = url_for('main.dashboard')

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if not (user and user.check_password(form.password.data)):
			flash('Invalid email or password', 'error')
			return redirect(url_for('auth.login'))
		login_user(user, remember=form.remember_me.data)
		session.permanent = True
		flash('Welcome back, {}!'.format(user.first_name), 'success')
		return redirect(next_page)

	return render_template('auth/login.html', title='Sign in', form=form)


@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))
	form = RegistrationForm()

	if form.validate_on_submit():
		first_name = form.first_name.data[0].upper() + form.first_name.data[1:]
		last_name = form.last_name.data[0].upper() + form.last_name.data[1:]
		user = User(email=form.email.data, first_name=first_name, last_name=last_name)
		user.set_password(form.password.data)
		user.generate_verification_token()
		db.session.add(user)
		db.session.flush()

		settings = UserSettings(user_id=user.user_id)
		db.session.add(settings)

		category_names = Category.load_initial_categories()
		for category_name in category_names:
			category = Category(user_id=user.user_id, category_name=category_name)
			db.session.add(category)

		db.session.commit()
		send_verification_email(user)
		flash('Account created! Please check your email to verify your account.', 'success')
		return redirect(url_for('auth.login'))

	return render_template('auth/register.html', title='Register', form=form)


@bp.route('/verify/<token>')
def verify_email(token):
	user = User.verify_email_token(token)
	if not user:
		flash('Invalid or expired verification link.', 'error')
		return redirect(url_for('auth.login'))
	user.email_verified = True
	user.verification_token = None
	db.session.commit()
	flash('Email verified successfully! You can now sign in.', 'success')
	return redirect(url_for('auth.login'))


@bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
	if current_user.is_authenticated and current_user.email_verified:
		return redirect(url_for('main.dashboard'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and not user.email_verified:
			send_verification_email(user)
			flash('Verification email sent.', 'success')
		else:
			flash('No unverified account found for this email.', 'error')
		return redirect(url_for('auth.login'))
	return render_template('auth/resend_verification.html', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))

	form = ResetPasswordRequestForm()

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if not user:
			flash('This email does not have an account associated with it', 'error')
		else:
			send_password_request_email(user)
			flash('Password reset email has been sent to {}'.format(form.email.data), 'success')
			return redirect(url_for('auth.login'))

	return render_template('auth/reset_password_request.html', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.dashboard'))

	user = User.verify_password_reset_token(token)
	if not user:
		flash('Invalid or expired reset link.', 'error')
		return redirect(url_for('auth.login'))

	form = ResetPasswordForm()

	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password has been reset', 'success')
		return redirect(url_for('auth.login'))

	return render_template('auth/reset_password.html', form=form)
