"""Add performance indexes for critical tables

Revision ID: 20250106_003
Revises: 20250101_002
Create Date: 2025-01-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250106_003'
down_revision = '20250101_002'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes to improve query performance"""
    
    # Users table indexes
    op.create_index('idx_users_phone', 'users', ['phone'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_kyc_status', 'users', ['kyc_status'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # User profiles indexes
    op.create_index('idx_user_profiles_user_id', 'user_profiles', ['user_id'])
    
    # Auth sessions indexes
    op.create_index('idx_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('idx_auth_sessions_expires_at', 'auth_sessions', ['expires_at'])
    op.create_index('idx_auth_sessions_token_hash', 'auth_sessions', ['token_hash'])
    
    # Trading accounts indexes
    op.create_index('idx_trading_accounts_user_id', 'trading_accounts', ['user_id'])
    op.create_index('idx_trading_accounts_account_number', 'trading_accounts', ['account_number'])
    op.create_index('idx_trading_accounts_status', 'trading_accounts', ['status'])
    
    # Trading orders indexes
    op.create_index('idx_trading_orders_user_id', 'trading_orders', ['user_id'])
    op.create_index('idx_trading_orders_account_id', 'trading_orders', ['account_id'])
    op.create_index('idx_trading_orders_symbol', 'trading_orders', ['symbol'])
    op.create_index('idx_trading_orders_status', 'trading_orders', ['status'])
    op.create_index('idx_trading_orders_created_at', 'trading_orders', ['created_at'])
    # Composite index for common queries
    op.create_index('idx_trading_orders_user_status', 'trading_orders', ['user_id', 'status'])
    op.create_index('idx_trading_orders_symbol_status', 'trading_orders', ['symbol', 'status'])
    
    # Financial transactions indexes
    op.create_index('idx_financial_transactions_user_id', 'financial_transactions', ['user_id'])
    op.create_index('idx_financial_transactions_account_id', 'financial_transactions', ['account_id'])
    op.create_index('idx_financial_transactions_type', 'financial_transactions', ['transaction_type'])
    op.create_index('idx_financial_transactions_status', 'financial_transactions', ['status'])
    op.create_index('idx_financial_transactions_created_at', 'financial_transactions', ['created_at'])
    # Composite index for user transaction history
    op.create_index('idx_financial_transactions_user_type', 'financial_transactions', ['user_id', 'transaction_type'])
    
    # Portfolio holdings indexes
    op.create_index('idx_portfolio_holdings_user_id', 'portfolio_holdings', ['user_id'])
    op.create_index('idx_portfolio_holdings_account_id', 'portfolio_holdings', ['account_id'])
    op.create_index('idx_portfolio_holdings_symbol', 'portfolio_holdings', ['symbol'])
    # Composite index for portfolio queries
    op.create_index('idx_portfolio_holdings_user_symbol', 'portfolio_holdings', ['user_id', 'symbol'])
    
    # Risk metrics indexes
    op.create_index('idx_risk_metrics_user_id', 'risk_metrics', ['user_id'])
    op.create_index('idx_risk_metrics_account_id', 'risk_metrics', ['account_id'])
    op.create_index('idx_risk_metrics_calculated_at', 'risk_metrics', ['calculated_at'])
    
    # Compliance records indexes
    op.create_index('idx_compliance_records_user_id', 'compliance_records', ['user_id'])
    op.create_index('idx_compliance_records_type', 'compliance_records', ['compliance_type'])
    op.create_index('idx_compliance_records_status', 'compliance_records', ['status'])
    op.create_index('idx_compliance_records_created_at', 'compliance_records', ['created_at'])
    
    # Audit trails indexes
    op.create_index('idx_audit_trails_user_id', 'audit_trails', ['user_id'])
    op.create_index('idx_audit_trails_action', 'audit_trails', ['action'])
    op.create_index('idx_audit_trails_resource_type', 'audit_trails', ['resource_type'])
    op.create_index('idx_audit_trails_created_at', 'audit_trails', ['created_at'])
    # Composite index for audit queries
    op.create_index('idx_audit_trails_user_action', 'audit_trails', ['user_id', 'action'])
    
    # Referral records indexes
    op.create_index('idx_referral_records_referrer_id', 'referral_records', ['referrer_id'])
    op.create_index('idx_referral_records_referred_id', 'referral_records', ['referred_user_id'])
    op.create_index('idx_referral_records_status', 'referral_records', ['status'])
    op.create_index('idx_referral_records_created_at', 'referral_records', ['created_at'])


def downgrade():
    """Remove performance indexes"""
    
    # Users table indexes
    op.drop_index('idx_users_phone', 'users')
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_kyc_status', 'users')
    op.drop_index('idx_users_created_at', 'users')
    
    # User profiles indexes
    op.drop_index('idx_user_profiles_user_id', 'user_profiles')
    
    # Auth sessions indexes
    op.drop_index('idx_auth_sessions_user_id', 'auth_sessions')
    op.drop_index('idx_auth_sessions_expires_at', 'auth_sessions')
    op.drop_index('idx_auth_sessions_token_hash', 'auth_sessions')
    
    # Trading accounts indexes
    op.drop_index('idx_trading_accounts_user_id', 'trading_accounts')
    op.drop_index('idx_trading_accounts_account_number', 'trading_accounts')
    op.drop_index('idx_trading_accounts_status', 'trading_accounts')
    
    # Trading orders indexes
    op.drop_index('idx_trading_orders_user_id', 'trading_orders')
    op.drop_index('idx_trading_orders_account_id', 'trading_orders')
    op.drop_index('idx_trading_orders_symbol', 'trading_orders')
    op.drop_index('idx_trading_orders_status', 'trading_orders')
    op.drop_index('idx_trading_orders_created_at', 'trading_orders')
    op.drop_index('idx_trading_orders_user_status', 'trading_orders')
    op.drop_index('idx_trading_orders_symbol_status', 'trading_orders')
    
    # Financial transactions indexes
    op.drop_index('idx_financial_transactions_user_id', 'financial_transactions')
    op.drop_index('idx_financial_transactions_account_id', 'financial_transactions')
    op.drop_index('idx_financial_transactions_type', 'financial_transactions')
    op.drop_index('idx_financial_transactions_status', 'financial_transactions')
    op.drop_index('idx_financial_transactions_created_at', 'financial_transactions')
    op.drop_index('idx_financial_transactions_user_type', 'financial_transactions')
    
    # Portfolio holdings indexes
    op.drop_index('idx_portfolio_holdings_user_id', 'portfolio_holdings')
    op.drop_index('idx_portfolio_holdings_account_id', 'portfolio_holdings')
    op.drop_index('idx_portfolio_holdings_symbol', 'portfolio_holdings')
    op.drop_index('idx_portfolio_holdings_user_symbol', 'portfolio_holdings')
    
    # Risk metrics indexes
    op.drop_index('idx_risk_metrics_user_id', 'risk_metrics')
    op.drop_index('idx_risk_metrics_account_id', 'risk_metrics')
    op.drop_index('idx_risk_metrics_calculated_at', 'risk_metrics')
    
    # Compliance records indexes
    op.drop_index('idx_compliance_records_user_id', 'compliance_records')
    op.drop_index('idx_compliance_records_type', 'compliance_records')
    op.drop_index('idx_compliance_records_status', 'compliance_records')
    op.drop_index('idx_compliance_records_created_at', 'compliance_records')
    
    # Audit trails indexes
    op.drop_index('idx_audit_trails_user_id', 'audit_trails')
    op.drop_index('idx_audit_trails_action', 'audit_trails')
    op.drop_index('idx_audit_trails_resource_type', 'audit_trails')
    op.drop_index('idx_audit_trails_created_at', 'audit_trails')
    op.drop_index('idx_audit_trails_user_action', 'audit_trails')
    
    # Referral records indexes
    op.drop_index('idx_referral_records_referrer_id', 'referral_records')
    op.drop_index('idx_referral_records_referred_id', 'referral_records')
    op.drop_index('idx_referral_records_status', 'referral_records')
    op.drop_index('idx_referral_records_created_at', 'referral_records')
