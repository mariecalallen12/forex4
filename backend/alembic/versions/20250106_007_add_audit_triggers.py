"""Add audit triggers for automatic change tracking

Revision ID: 007
Revises: 006
Create Date: 2025-12-06 09:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Add audit triggers to critical tables for automatic change tracking"""
    
    # Create audit trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_trigger_function()
        RETURNS TRIGGER AS $$
        DECLARE
            old_data json;
            new_data json;
            changed_fields json;
        BEGIN
            -- For INSERT operations
            IF (TG_OP = 'INSERT') THEN
                INSERT INTO audit_trails (
                    user_id,
                    action,
                    table_name,
                    record_id,
                    new_data,
                    ip_address,
                    user_agent,
                    timestamp
                ) VALUES (
                    COALESCE(current_setting('app.current_user_id', true)::INTEGER, NULL),
                    'INSERT',
                    TG_TABLE_NAME,
                    NEW.id,
                    row_to_json(NEW),
                    current_setting('app.client_ip', true),
                    current_setting('app.user_agent', true),
                    NOW()
                );
                RETURN NEW;
                
            -- For UPDATE operations
            ELSIF (TG_OP = 'UPDATE') THEN
                -- Calculate changed fields
                SELECT json_object_agg(key, value)
                INTO changed_fields
                FROM (
                    SELECT key, value
                    FROM json_each(row_to_json(NEW))
                    WHERE value IS DISTINCT FROM (row_to_json(OLD) ->> key)::json
                ) AS changes;
                
                -- Only log if there are actual changes
                IF changed_fields IS NOT NULL THEN
                    INSERT INTO audit_trails (
                        user_id,
                        action,
                        table_name,
                        record_id,
                        old_data,
                        new_data,
                        changed_fields,
                        ip_address,
                        user_agent,
                        timestamp
                    ) VALUES (
                        COALESCE(current_setting('app.current_user_id', true)::INTEGER, NULL),
                        'UPDATE',
                        TG_TABLE_NAME,
                        NEW.id,
                        row_to_json(OLD),
                        row_to_json(NEW),
                        changed_fields,
                        current_setting('app.client_ip', true),
                        current_setting('app.user_agent', true),
                        NOW()
                    );
                END IF;
                RETURN NEW;
                
            -- For DELETE operations
            ELSIF (TG_OP = 'DELETE') THEN
                INSERT INTO audit_trails (
                    user_id,
                    action,
                    table_name,
                    record_id,
                    old_data,
                    ip_address,
                    user_agent,
                    timestamp
                ) VALUES (
                    COALESCE(current_setting('app.current_user_id', true)::INTEGER, NULL),
                    'DELETE',
                    TG_TABLE_NAME,
                    OLD.id,
                    row_to_json(OLD),
                    current_setting('app.client_ip', true),
                    current_setting('app.user_agent', true),
                    NOW()
                );
                RETURN OLD;
            END IF;
            
            RETURN NULL;
        EXCEPTION WHEN OTHERS THEN
            -- Log error but don't fail the original operation
            RAISE WARNING 'Audit trigger failed: %', SQLERRM;
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    # Add trigger to users table
    op.execute("""
        CREATE TRIGGER audit_users_trigger
        AFTER INSERT OR UPDATE OR DELETE ON users
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to user_profiles table
    op.execute("""
        CREATE TRIGGER audit_user_profiles_trigger
        AFTER INSERT OR UPDATE OR DELETE ON user_profiles
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to trading_accounts table
    op.execute("""
        CREATE TRIGGER audit_trading_accounts_trigger
        AFTER INSERT OR UPDATE OR DELETE ON trading_accounts
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to trading_orders table
    op.execute("""
        CREATE TRIGGER audit_trading_orders_trigger
        AFTER INSERT OR UPDATE OR DELETE ON trading_orders
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to financial_transactions table
    op.execute("""
        CREATE TRIGGER audit_financial_transactions_trigger
        AFTER INSERT OR UPDATE OR DELETE ON financial_transactions
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to compliance_records table
    op.execute("""
        CREATE TRIGGER audit_compliance_records_trigger
        AFTER INSERT OR UPDATE OR DELETE ON compliance_records
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to portfolio_holdings table
    op.execute("""
        CREATE TRIGGER audit_portfolio_holdings_trigger
        AFTER INSERT OR UPDATE OR DELETE ON portfolio_holdings
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to risk_metrics table (if exists)
    op.execute("""
        CREATE TRIGGER audit_risk_metrics_trigger
        AFTER INSERT OR UPDATE OR DELETE ON risk_metrics
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Add trigger to referral_records table
    op.execute("""
        CREATE TRIGGER audit_referral_records_trigger
        AFTER INSERT OR UPDATE OR DELETE ON referral_records
        FOR EACH ROW
        EXECUTE FUNCTION audit_trigger_function();
    """)
    
    # Create index on audit_trails for better query performance
    op.create_index(
        'idx_audit_trails_timestamp',
        'audit_trails',
        ['timestamp']
    )
    
    op.create_index(
        'idx_audit_trails_user_action',
        'audit_trails',
        ['user_id', 'action', 'timestamp']
    )
    
    op.create_index(
        'idx_audit_trails_table_record',
        'audit_trails',
        ['table_name', 'record_id', 'timestamp']
    )
    
    # Add comments for documentation
    op.execute("""
        COMMENT ON FUNCTION audit_trigger_function() IS 
        'Automatically logs all INSERT, UPDATE, DELETE operations to audit_trails table. 
        Captures old_data, new_data, changed_fields, user_id, ip_address, and user_agent.
        Gracefully handles errors to prevent blocking main operations.';
    """)


def downgrade():
    """Remove audit triggers"""
    
    # Drop all triggers
    op.execute("DROP TRIGGER IF EXISTS audit_users_trigger ON users;")
    op.execute("DROP TRIGGER IF EXISTS audit_user_profiles_trigger ON user_profiles;")
    op.execute("DROP TRIGGER IF EXISTS audit_trading_accounts_trigger ON trading_accounts;")
    op.execute("DROP TRIGGER IF EXISTS audit_trading_orders_trigger ON trading_orders;")
    op.execute("DROP TRIGGER IF EXISTS audit_financial_transactions_trigger ON financial_transactions;")
    op.execute("DROP TRIGGER IF EXISTS audit_compliance_records_trigger ON compliance_records;")
    op.execute("DROP TRIGGER IF EXISTS audit_portfolio_holdings_trigger ON portfolio_holdings;")
    op.execute("DROP TRIGGER IF EXISTS audit_risk_metrics_trigger ON risk_metrics;")
    op.execute("DROP TRIGGER IF EXISTS audit_referral_records_trigger ON referral_records;")
    
    # Drop indexes
    op.drop_index('idx_audit_trails_table_record', table_name='audit_trails')
    op.drop_index('idx_audit_trails_user_action', table_name='audit_trails')
    op.drop_index('idx_audit_trails_timestamp', table_name='audit_trails')
    
    # Drop the trigger function
    op.execute("DROP FUNCTION IF EXISTS audit_trigger_function();")
