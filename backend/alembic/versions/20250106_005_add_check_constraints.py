"""Add check constraints for data validation

Revision ID: 20250106_005
Revises: 20250106_004
Create Date: 2025-01-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250106_005'
down_revision = '20250106_004'
branch_labels = None
depends_on = None


def upgrade():
    """Add check constraints to validate data at database level"""
    
    # Trading accounts - balance must be non-negative
    op.create_check_constraint(
        'ck_trading_accounts_balance_positive',
        'trading_accounts',
        'balance >= 0'
    )
    
    # Trading accounts - leverage ratio must be >= 1
    op.create_check_constraint(
        'ck_trading_accounts_leverage_min',
        'trading_accounts',
        'leverage_ratio >= 1.0'
    )
    
    # Trading orders - quantity must be positive
    op.create_check_constraint(
        'ck_trading_orders_quantity_positive',
        'trading_orders',
        'quantity > 0'
    )
    
    # Trading orders - executed quantity must be non-negative and <= quantity
    op.create_check_constraint(
        'ck_trading_orders_executed_quantity',
        'trading_orders',
        'executed_quantity >= 0 AND executed_quantity <= quantity'
    )
    
    # Trading orders - price must be positive (when not NULL)
    op.create_check_constraint(
        'ck_trading_orders_price_positive',
        'trading_orders',
        'price IS NULL OR price > 0'
    )
    
    # Trading orders - stop price must be positive (when not NULL)
    op.create_check_constraint(
        'ck_trading_orders_stop_price_positive',
        'trading_orders',
        'stop_price IS NULL OR stop_price > 0'
    )
    
    # Trading orders - average price must be positive (when not NULL)
    op.create_check_constraint(
        'ck_trading_orders_avg_price_positive',
        'trading_orders',
        'average_price IS NULL OR average_price > 0'
    )
    
    # Financial transactions - amount must not be zero
    op.create_check_constraint(
        'ck_financial_transactions_amount_nonzero',
        'financial_transactions',
        'amount != 0'
    )
    
    # Portfolio holdings - quantity must not be zero
    op.create_check_constraint(
        'ck_portfolio_holdings_quantity_nonzero',
        'portfolio_holdings',
        'quantity != 0'
    )
    
    # Portfolio holdings - average cost must be positive
    op.create_check_constraint(
        'ck_portfolio_holdings_avg_cost_positive',
        'portfolio_holdings',
        'average_cost > 0'
    )
    
    # Portfolio holdings - current price must be positive (when not NULL)
    op.create_check_constraint(
        'ck_portfolio_holdings_current_price',
        'portfolio_holdings',
        'current_price IS NULL OR current_price > 0'
    )
    
    # Risk metrics - Value at Risk must be non-negative (when not NULL)
    op.create_check_constraint(
        'ck_risk_metrics_var_1d',
        'risk_metrics',
        'var_1d IS NULL OR var_1d >= 0'
    )
    
    op.create_check_constraint(
        'ck_risk_metrics_var_1w',
        'risk_metrics',
        'var_1w IS NULL OR var_1w >= 0'
    )
    
    # Risk metrics - max drawdown must be between 0 and 1 (percentage)
    op.create_check_constraint(
        'ck_risk_metrics_max_drawdown',
        'risk_metrics',
        'max_drawdown IS NULL OR (max_drawdown >= 0 AND max_drawdown <= 1)'
    )
    
    # Compliance records - KYC level must be between 0 and 3
    op.create_check_constraint(
        'ck_compliance_records_kyc_level',
        'compliance_records',
        'kyc_level IS NULL OR (kyc_level >= 0 AND kyc_level <= 3)'
    )
    
    # Referral records - commission rate must be between 0 and 1
    op.create_check_constraint(
        'ck_referral_records_commission_rate',
        'referral_records',
        'commission_rate >= 0 AND commission_rate <= 1'
    )


def downgrade():
    """Remove check constraints"""
    
    # Trading accounts
    op.drop_constraint('ck_trading_accounts_balance_positive', 'trading_accounts')
    op.drop_constraint('ck_trading_accounts_leverage_min', 'trading_accounts')
    
    # Trading orders
    op.drop_constraint('ck_trading_orders_quantity_positive', 'trading_orders')
    op.drop_constraint('ck_trading_orders_executed_quantity', 'trading_orders')
    op.drop_constraint('ck_trading_orders_price_positive', 'trading_orders')
    op.drop_constraint('ck_trading_orders_stop_price_positive', 'trading_orders')
    op.drop_constraint('ck_trading_orders_avg_price_positive', 'trading_orders')
    
    # Financial transactions
    op.drop_constraint('ck_financial_transactions_amount_nonzero', 'financial_transactions')
    
    # Portfolio holdings
    op.drop_constraint('ck_portfolio_holdings_quantity_nonzero', 'portfolio_holdings')
    op.drop_constraint('ck_portfolio_holdings_avg_cost_positive', 'portfolio_holdings')
    op.drop_constraint('ck_portfolio_holdings_current_price', 'portfolio_holdings')
    
    # Risk metrics
    op.drop_constraint('ck_risk_metrics_var_1d', 'risk_metrics')
    op.drop_constraint('ck_risk_metrics_var_1w', 'risk_metrics')
    op.drop_constraint('ck_risk_metrics_max_drawdown', 'risk_metrics')
    
    # Compliance records
    op.drop_constraint('ck_compliance_records_kyc_level', 'compliance_records')
    
    # Referral records
    op.drop_constraint('ck_referral_records_commission_rate', 'referral_records')
