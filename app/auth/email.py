from flask import render_template, current_app, url_for
from app.email import send_email


def send_password_request_email(user):
	token = user.get_password_reset_token()
	subject = "Finance Manager - Password reset"
	sender = current_app.config['ADMINS'][0]
	recipients = [user.email]
	text_body = render_template('email/reset_password.txt', user=user, token=token)
	html_body = render_template('email/reset_password.html', user=user, token=token)
	send_email(subject, sender, recipients, text_body, html_body)


def send_verification_email(user):
	token = user.get_email_verification_token()
	subject = "Finance Manager - Verify your email"
	sender = current_app.config['ADMINS'][0]
	recipients = [user.email]
	verify_url = url_for('auth.verify_email', token=token, _external=True)
	text_body = render_template('email/verify_email.txt', user=user, verify_url=verify_url)
	html_body = render_template('email/verify_email.html', user=user, verify_url=verify_url)
	send_email(subject, sender, recipients, text_body, html_body)
