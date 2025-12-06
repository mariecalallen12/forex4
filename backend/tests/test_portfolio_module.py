"""
Tests for Portfolio Module
Covers portfolio management, holdings, and performance tracking
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestPortfolioModule:
    """Test suite for portfolio operations"""
    
    def test_get_portfolio_overview(self, client: TestClient, auth_headers: dict):
        """Test retrieving portfolio overview"""
        response = client.get(
            "/api/portfolio/overview",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Portfolio should contain total_value, holdings_count, etc.
    
    def test_get_holdings(self, client: TestClient, auth_headers: dict):
        """Test retrieving all holdings"""
        response = client.get(
            "/api/portfolio/holdings",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_add_holding(self, client: TestClient, auth_headers: dict):
        """Test adding a new holding to portfolio"""
        holding_data = {
            "symbol": "BTCUSD",
            "quantity": 0.5,
            "average_cost": 45000.00
        }
        
        response = client.post(
            "/api/portfolio/holdings",
            json=holding_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["symbol"] == "BTCUSD"
        assert data["quantity"] == 0.5
    
    def test_update_holding(self, client: TestClient, auth_headers: dict):
        """Test updating an existing holding"""
        update_data = {
            "symbol": "BTCUSD",
            "quantity": 0.75,
            "average_cost": 46000.00
        }
        
        response = client.put(
            "/api/portfolio/holdings",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]
    
    def test_delete_holding(self, client: TestClient, auth_headers: dict):
        """Test removing a holding from portfolio"""
        symbol = "ETHUSD"
        
        response = client.delete(
            f"/api/portfolio/holdings/{symbol}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204, 404]
    
    def test_get_portfolio_performance(self, client: TestClient, auth_headers: dict):
        """Test retrieving portfolio performance metrics"""
        response = client.get(
            "/api/portfolio/performance?period=1y",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain metrics like total_return, daily_return, etc.
    
    def test_get_portfolio_performance_daily(self, client: TestClient, auth_headers: dict):
        """Test retrieving daily portfolio performance"""
        response = client.get(
            "/api/portfolio/performance?period=1d",
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_get_portfolio_analytics(self, client: TestClient, auth_headers: dict):
        """Test retrieving portfolio analytics"""
        response = client.get(
            "/api/portfolio/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain diversification, risk metrics, etc.
    
    def test_rebalance_portfolio(self, client: TestClient, auth_headers: dict):
        """Test portfolio rebalancing"""
        rebalance_data = {
            "target_allocation": {
                "BTC": 0.4,
                "ETH": 0.3,
                "USD": 0.3
            }
        }
        
        response = client.post(
            "/api/portfolio/rebalance",
            json=rebalance_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201, 202]  # 202 for async processing
    
    def test_get_portfolio_history(self, client: TestClient, auth_headers: dict):
        """Test retrieving portfolio value history"""
        response = client.get(
            "/api/portfolio/history?days=30",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    def test_get_holding_details(self, client: TestClient, auth_headers: dict):
        """Test retrieving details for a specific holding"""
        symbol = "BTCUSD"
        
        response = client.get(
            f"/api/portfolio/holdings/{symbol}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
    
    def test_calculate_portfolio_metrics(self, client: TestClient, auth_headers: dict):
        """Test calculating various portfolio metrics"""
        response = client.get(
            "/api/portfolio/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should include Sharpe ratio, volatility, etc.
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
    return {
        "Authorization": "Bearer test_token_here"
    }
