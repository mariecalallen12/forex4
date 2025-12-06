"""Add foreign key constraints for referential integrity

Revision ID: 20250106_004
Revises: 20250106_003
Create Date: 2025-01-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250106_004'
down_revision = '20250106_003'
branch_labels = None
depends_on = None


def upgrade():
    """Add foreign key constraints to ensure referential integrity"""
    
    # User profiles foreign key
    op.create_foreign_key(
        'fk_user_profiles_user_id',
        'user_profiles', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Auth sessions foreign key
    op.create_foreign_key(
        'fk_auth_sessions_user_id',
        'auth_sessions', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Trading accounts foreign key
    op.create_foreign_key(
        'fk_trading_accounts_user_id',
        'trading_accounts', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Trading orders foreign keys
    op.create_foreign_key(
        'fk_trading_orders_user_id',
        'trading_orders', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_trading_orders_account_id',
        'trading_orders', 'trading_accounts',
        ['account_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Financial transactions foreign keys
    op.create_foreign_key(
        'fk_financial_transactions_user_id',
        'financial_transactions', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_financial_transactions_account_id',
        'financial_transactions', 'trading_accounts',
        ['account_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Portfolio holdings foreign keys
    op.create_foreign_key(
        'fk_portfolio_holdings_user_id',
        'portfolio_holdings', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_portfolio_holdings_account_id',
        'portfolio_holdings', 'trading_accounts',
        ['account_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Risk metrics foreign keys
    op.create_foreign_key(
        'fk_risk_metrics_user_id',
        'risk_metrics', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_risk_metrics_account_id',
        'risk_metrics', 'trading_accounts',
        ['account_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Compliance records foreign key
    op.create_foreign_key(
        'fk_compliance_records_user_id',
        'compliance_records', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Audit trails foreign key
    op.create_foreign_key(
        'fk_audit_trails_user_id',
        'audit_trails', 'users',
        ['user_id'], ['id'],
        ondelete='SET NULL'  # Keep audit logs even if user is deleted
    )
    
    # Referral records foreign keys
    op.create_foreign_key(
        'fk_referral_records_referrer_id',
        'referral_records', 'users',
        ['referrer_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_referral_records_referred_user_id',
        'referral_records', 'users',
        ['referred_user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    """Remove foreign key constraints"""
    
    # User profiles
    op.drop_constraint('fk_user_profiles_user_id', 'user_profiles', type_='foreignkey')
    
    # Auth sessions
    op.drop_constraint('fk_auth_sessions_user_id', 'auth_sessions', type_='foreignkey')
    
    # Trading accounts
    op.drop_constraint('fk_trading_accounts_user_id', 'trading_accounts', type_='foreignkey')
    
    # Trading orders
    op.drop_constraint('fk_trading_orders_user_id', 'trading_orders', type_='foreignkey')
    op.drop_constraint('fk_trading_orders_account_id', 'trading_orders', type_='foreignkey')
    
    # Financial transactions
    op.drop_constraint('fk_financial_transactions_user_id', 'financial_transactions', type_='foreignkey')
    op.drop_constraint('fk_financial_transactions_account_id', 'financial_transactions', type_='foreignkey')
    
    # Portfolio holdings
    op.drop_constraint('fk_portfolio_holdings_user_id', 'portfolio_holdings', type_='foreignkey')
    op.drop_constraint('fk_portfolio_holdings_account_id', 'portfolio_holdings', type_='foreignkey')
    
    # Risk metrics
    op.drop_constraint('fk_risk_metrics_user_id', 'risk_metrics', type_='foreignkey')
    op.drop_constraint('fk_risk_metrics_account_id', 'risk_metrics', type_='foreignkey')
    
    # Compliance records
    op.drop_constraint('fk_compliance_records_user_id', 'compliance_records', type_='foreignkey')
    
    # Audit trails
    op.drop_constraint('fk_audit_trails_user_id', 'audit_trails', type_='foreignkey')
    
    # Referral records
    op.drop_constraint('fk_referral_records_referrer_id', 'referral_records', type_='foreignkey')
    op.drop_constraint('fk_referral_records_referred_user_id', 'referral_records', type_='foreignkey')
