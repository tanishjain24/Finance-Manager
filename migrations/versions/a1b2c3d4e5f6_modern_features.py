"""Add modern features: settings, budgets, savings, bills, email verification"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'dd7913713709'
branch_labels = None
depends_on = None


def upgrade():
	op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=True))
	op.add_column('user', sa.Column('verification_token', sa.String(length=128), nullable=True))
	op.add_column('account', sa.Column('account_type', sa.String(length=20), nullable=True))

	op.create_table('user_settings',
		sa.Column('settings_id', sa.Integer(), nullable=False),
		sa.Column('user_id', sa.Integer(), nullable=True),
		sa.Column('currency', sa.String(length=3), nullable=True),
		sa.Column('theme', sa.String(length=10), nullable=True),
		sa.Column('notifications_enabled', sa.Boolean(), nullable=True),
		sa.Column('email_notifications', sa.Boolean(), nullable=True),
		sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name=op.f('fk_user_settings_user_id_user')),
		sa.PrimaryKeyConstraint('settings_id', name=op.f('pk_user_settings')),
		sa.UniqueConstraint('user_id', name=op.f('uq_user_settings_user_id')),
	)

	op.create_table('budget',
		sa.Column('budget_id', sa.Integer(), nullable=False),
		sa.Column('user_id', sa.Integer(), nullable=True),
		sa.Column('category_id', sa.Integer(), nullable=True),
		sa.Column('amount', sa.Numeric(scale=2), nullable=True),
		sa.Column('month', sa.Integer(), nullable=True),
		sa.Column('year', sa.Integer(), nullable=True),
		sa.ForeignKeyConstraint(['category_id'], ['category.category_id'], name=op.f('fk_budget_category_id_category')),
		sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name=op.f('fk_budget_user_id_user')),
		sa.PrimaryKeyConstraint('budget_id', name=op.f('pk_budget')),
	)

	op.create_table('savings_goal',
		sa.Column('goal_id', sa.Integer(), nullable=False),
		sa.Column('user_id', sa.Integer(), nullable=True),
		sa.Column('name', sa.String(length=64), nullable=True),
		sa.Column('target_amount', sa.Numeric(scale=2), nullable=True),
		sa.Column('current_amount', sa.Numeric(scale=2), nullable=True),
		sa.Column('deadline', sa.DateTime(), nullable=True),
		sa.Column('icon', sa.String(length=10), nullable=True),
		sa.Column('color', sa.String(length=20), nullable=True),
		sa.Column('created_at', sa.DateTime(), nullable=True),
		sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name=op.f('fk_savings_goal_user_id_user')),
		sa.PrimaryKeyConstraint('goal_id', name=op.f('pk_savings_goal')),
	)

	op.create_table('bill_reminder',
		sa.Column('bill_id', sa.Integer(), nullable=False),
		sa.Column('user_id', sa.Integer(), nullable=True),
		sa.Column('name', sa.String(length=64), nullable=True),
		sa.Column('amount', sa.Numeric(scale=2), nullable=True),
		sa.Column('due_date', sa.DateTime(), nullable=True),
		sa.Column('recurring', sa.Boolean(), nullable=True),
		sa.Column('recurring_interval', sa.String(length=20), nullable=True),
		sa.Column('is_paid', sa.Boolean(), nullable=True),
		sa.Column('created_at', sa.DateTime(), nullable=True),
		sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name=op.f('fk_bill_reminder_user_id_user')),
		sa.PrimaryKeyConstraint('bill_id', name=op.f('pk_bill_reminder')),
	)

	op.execute("UPDATE user SET email_verified = 1 WHERE email_verified IS NULL")
	op.execute("UPDATE account SET account_type = 'bank' WHERE account_type IS NULL")


def downgrade():
	op.drop_table('bill_reminder')
	op.drop_table('savings_goal')
	op.drop_table('budget')
	op.drop_table('user_settings')
	op.drop_column('account', 'account_type')
	op.drop_column('user', 'verification_token')
	op.drop_column('user', 'email_verified')
