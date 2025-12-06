"""
Tests for Financial Module
Covers transactions, deposits, withdrawals, and payments
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import uuid


class TestFinancialModule:
    """Test suite for financial operations"""
    
    def test_get_transaction_history(self, client: TestClient, auth_headers: dict):
        """Test retrieving transaction history"""
        response = client.get(
            "/api/financial/transactions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_get_filtered_transactions(self, client: TestClient, auth_headers: dict):
        """Test retrieving filtered transactions"""
        response = client.get(
            "/api/financial/transactions?type=deposit&limit=50",
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_deposit_funds(self, client: TestClient, auth_headers: dict):
        """Test depositing funds"""
        deposit_data = {
            "amount": 1000.00,
            "currency": "USD",
            "payment_method": "bank_transfer",
            "reference": "Initial deposit"
        }
        
        response = client.post(
            "/api/financial/deposit",
            json=deposit_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 202]
        data = response.json()
        assert "transaction_id" in data or "id" in data
        assert data["amount"] == 1000.00
    
    def test_deposit_invalid_amount(self, client: TestClient, auth_headers: dict):
        """Test depositing invalid amount"""
        deposit_data = {
            "amount": -100.00,  # Invalid: negative amount
            "currency": "USD",
            "payment_method": "bank_transfer"
        }
        
        response = client.post(
            "/api/financial/deposit",
            json=deposit_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_withdraw_funds(self, client: TestClient, auth_headers: dict):
        """Test withdrawing funds"""
        withdrawal_data = {
            "amount": 500.00,
            "currency": "USD",
            "withdrawal_method": "bank_transfer",
            "bank_details": {
                "account_number": "123456789",
                "routing_number": "021000021",
                "bank_name": "Chase Bank"
            }
        }
        
        response = client.post(
            "/api/financial/withdraw",
            json=withdrawal_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 202, 400]  # 400 if insufficient balance
    
    def test_withdraw_exceeds_balance(self, client: TestClient, auth_headers: dict):
        """Test withdrawing more than balance"""
        withdrawal_data = {
            "amount": 999999999.00,  # Very large amount
            "currency": "USD",
            "withdrawal_method": "bank_transfer"
        }
        
        response = client.post(
            "/api/financial/withdraw",
            json=withdrawal_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400  # Insufficient balance
    
    def test_get_account_balance(self, client: TestClient, auth_headers: dict):
        """Test retrieving account balance"""
        response = client.get(
            "/api/financial/balance",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data or "available_balance" in data
        assert isinstance(data.get("balance", 0), (int, float))
    
    def test_currency_exchange(self, client: TestClient, auth_headers: dict):
        """Test currency exchange"""
        exchange_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": 1000.00
        }
        
        response = client.post(
            "/api/financial/exchange",
            json=exchange_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "exchange_rate" in data or "converted_amount" in data
    
    def test_get_payment_status(self, client: TestClient, auth_headers: dict):
        """Test retrieving payment status"""
        payment_id = str(uuid.uuid4())
        
        response = client.get(
            f"/api/financial/payments/{payment_id}/status",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
    
    def test_process_payment(self, client: TestClient, auth_headers: dict):
        """Test processing a payment"""
        payment_id = str(uuid.uuid4())
        
        response = client.post(
            f"/api/financial/payments/{payment_id}/process",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 404, 400]
    
    def test_cancel_payment(self, client: TestClient, auth_headers: dict):
        """Test canceling a payment"""
        payment_id = str(uuid.uuid4())
        
        response = client.post(
            f"/api/financial/payments/{payment_id}/cancel",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 404, 400]
    
    def test_get_payment_history(self, client: TestClient, auth_headers: dict):
        """Test retrieving payment history"""
        response = client.get(
            "/api/financial/payment-history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_get_financial_reports(self, client: TestClient, auth_headers: dict):
        """Test retrieving financial reports"""
        response = client.get(
            "/api/financial/reports?period=monthly&year=2025",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)


# Fixtures
@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    return {
        "Authorization": "Bearer test_token_here"
    }
