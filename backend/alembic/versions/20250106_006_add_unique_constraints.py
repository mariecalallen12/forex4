"""Add unique constraints for business logic

Revision ID: 20250106_006
Revises: 20250106_005
Create Date: 2025-01-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250106_006'
down_revision = '20250106_005'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique constraints to ensure data uniqueness for business logic"""
    
    # Users - phone number must be unique
    op.create_unique_constraint(
        'uq_users_phone',
        'users',
        ['phone']
    )
    
    # Users - email must be unique (when not NULL)
    op.create_unique_constraint(
        'uq_users_email',
        'users',
        ['email']
    )
    
    # Trading accounts - account number must be unique
    op.create_unique_constraint(
        'uq_trading_accounts_account_number',
        'trading_accounts',
        ['account_number']
    )
    
    # Auth sessions - token hash must be unique
    op.create_unique_constraint(
        'uq_auth_sessions_token_hash',
        'auth_sessions',
        ['token_hash']
    )
    
    # Referral records - each user can only be referred once
    op.create_unique_constraint(
        'uq_referral_records_referred_user_id',
        'referral_records',
        ['referred_user_id']
    )
    
    # Portfolio holdings - one holding per user-symbol combination
    op.create_unique_constraint(
        'uq_portfolio_holdings_user_symbol',
        'portfolio_holdings',
        ['user_id', 'symbol']
    )


def downgrade():
    """Remove unique constraints"""
    
    # Users
    op.drop_constraint('uq_users_phone', 'users', type_='unique')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    
    # Trading accounts
    op.drop_constraint('uq_trading_accounts_account_number', 'trading_accounts', type_='unique')
    
    # Auth sessions
    op.drop_constraint('uq_auth_sessions_token_hash', 'auth_sessions', type_='unique')
    
    # Referral records
    op.drop_constraint('uq_referral_records_referred_user_id', 'referral_records', type_='unique')
    
    # Portfolio holdings
    op.drop_constraint('uq_portfolio_holdings_user_symbol', 'portfolio_holdings', type_='unique')
