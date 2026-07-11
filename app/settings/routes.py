from app import db
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.settings import bp
from app.settings.forms import ProfileForm, ChangePasswordForm, PreferencesForm


@bp.route('/')
@login_required
def index():
	profile_form = ProfileForm(
		first_name=current_user.first_name,
		last_name=current_user.last_name,
		email=current_user.email,
	)
	password_form = ChangePasswordForm()
	settings = current_user.get_settings()
	prefs_form = PreferencesForm(
		currency=settings.currency,
		theme=settings.theme,
		notifications_enabled=settings.notifications_enabled,
		email_notifications=settings.email_notifications,
	)
	return render_template('settings/index.html',
		profile_form=profile_form,
		password_form=password_form,
		prefs_form=prefs_form,
	)


@bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
	form = ProfileForm()
	if form.validate_on_submit():
		current_user.first_name = form.first_name.data
		current_user.last_name = form.last_name.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Profile updated successfully.', 'success')
	return redirect(url_for('settings.index'))


@bp.route('/password', methods=['POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if not current_user.check_password(form.current_password.data):
			flash('Current password is incorrect.', 'error')
		else:
			current_user.set_password(form.password.data)
			db.session.commit()
			flash('Password changed successfully.', 'success')
	return redirect(url_for('settings.index'))


@bp.route('/preferences', methods=['POST'])
@login_required
def update_preferences():
	form = PreferencesForm()
	if form.validate_on_submit():
		settings = current_user.get_settings()
		settings.currency = form.currency.data
		settings.theme = form.theme.data
		settings.notifications_enabled = form.notifications_enabled.data
		settings.email_notifications = form.email_notifications.data
		db.session.commit()
		flash('Preferences saved.', 'success')
	return redirect(url_for('settings.index'))
