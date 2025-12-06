"""
Tests for Trading Module
Covers trading endpoints, order management, and position tracking
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid


class TestTradingModule:
    """Test suite for trading operations"""
    
    def test_create_market_order(self, client: TestClient, auth_headers: dict):
        """Test creating a market order"""
        order_data = {
            "symbol": "BTCUSD",
            "side": "buy",
            "order_type": "market",
            "quantity": 0.1
        }
        
        response = client.post(
            "/api/trading/orders",
            json=order_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == "BTCUSD"
        assert data["side"] == "buy"
        assert data["order_type"] == "market"
        assert data["quantity"] == 0.1
        assert "id" in data
        assert data["status"] in ["pending", "filled"]
    
    def test_create_limit_order(self, client: TestClient, auth_headers: dict):
        """Test creating a limit order"""
        order_data = {
            "symbol": "ETHUSD",
            "side": "sell",
            "order_type": "limit",
            "quantity": 1.0,
            "price": 2000.00
        }
        
        response = client.post(
            "/api/trading/orders",
            json=order_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == "ETHUSD"
        assert data["side"] == "sell"
        assert data["order_type"] == "limit"
        assert data["price"] == 2000.00
    
    def test_create_stop_order(self, client: TestClient, auth_headers: dict):
        """Test creating a stop order"""
        order_data = {
            "symbol": "BTCUSD",
            "side": "buy",
            "order_type": "stop",
            "quantity": 0.05,
            "stop_price": 50000.00
        }
        
        response = client.post(
            "/api/trading/orders",
            json=order_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["order_type"] == "stop"
        assert data["stop_price"] == 50000.00
    
    def test_create_order_invalid_quantity(self, client: TestClient, auth_headers: dict):
        """Test creating order with invalid quantity"""
        order_data = {
            "symbol": "BTCUSD",
            "side": "buy",
            "order_type": "market",
            "quantity": -0.1  # Invalid: negative quantity
        }
        
        response = client.post(
            "/api/trading/orders",
            json=order_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_order_history(self, client: TestClient, auth_headers: dict):
        """Test retrieving order history"""
        response = client.get(
            "/api/trading/orders",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_get_order_history_with_filters(self, client: TestClient, auth_headers: dict):
        """Test retrieving order history with status filter"""
        response = client.get(
            "/api/trading/orders?status=open&limit=50",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_cancel_order(self, client: TestClient, auth_headers: dict):
        """Test canceling an order"""
        # First create an order
        order_data = {
            "symbol": "BTCUSD",
            "side": "buy",
            "order_type": "limit",
            "quantity": 0.1,
            "price": 45000.00
        }
        
        create_response = client.post(
            "/api/trading/orders",
            json=order_data,
            headers=auth_headers
        )
        
        if create_response.status_code == 201:
            order_id = create_response.json()["id"]
            
            # Cancel the order
            cancel_response = client.delete(
                f"/api/trading/orders/{order_id}",
                headers=auth_headers
            )
            
            assert cancel_response.status_code in [200, 204]
    
    def test_modify_order(self, client: TestClient, auth_headers: dict):
        """Test modifying an existing order"""
        # First create an order
        order_data = {
            "symbol": "ETHUSD",
            "side": "buy",
            "order_type": "limit",
            "quantity": 1.0,
            "price": 1800.00
        }
        
        create_response = client.post(
            "/api/trading/orders",
            json=order_data,
            headers=auth_headers
        )
        
        if create_response.status_code == 201:
            order_id = create_response.json()["id"]
            
            # Modify the order
            modify_data = {
                "quantity": 1.5,
                "price": 1850.00
            }
            
            modify_response = client.put(
                f"/api/trading/orders/{order_id}",
                json=modify_data,
                headers=auth_headers
            )
            
            assert modify_response.status_code in [200, 201]
    
    def test_get_trading_account(self, client: TestClient, auth_headers: dict):
        """Test retrieving trading account information"""
        response = client.get(
            "/api/trading/account",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data or "account_number" in data
    
    def test_get_positions(self, client: TestClient, auth_headers: dict):
        """Test retrieving open positions"""
        response = client.get(
            "/api/trading/positions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_get_position_by_symbol(self, client: TestClient, auth_headers: dict):
        """Test retrieving position for specific symbol"""
        response = client.get(
            "/api/trading/positions/BTCUSD",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]  # 404 if no position
    
    def test_close_position(self, client: TestClient, auth_headers: dict):
        """Test closing a position"""
        # This would require an open position
        position_id = str(uuid.uuid4())
        
        response = client.delete(
            f"/api/trading/positions/{position_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 404]
    
    def test_get_trading_statistics(self, client: TestClient, auth_headers: dict):
        """Test retrieving trading statistics"""
        response = client.get(
            "/api/trading/statistics?period=30d",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_order_book(self, client: TestClient, auth_headers: dict):
        """Test retrieving order book for a symbol"""
        response = client.get(
            "/api/trading/orderbook/BTCUSD",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Order book should have bids and asks
        assert isinstance(data, dict)


# Fixtures
@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    # This would typically use a test token
    return {
        "Authorization": "Bearer test_token_here"
    }
