import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..dcf_model import DCFModel
from unittest.mock import patch, MagicMock
import json

client = TestClient(app)

@pytest.fixture
def mock_financial_data():
    return {
        "cashFlow": {
            "annualReports": [
                {
                    "fiscalDateEnding": "2023-12-31",
                    "operatingCashflow": 100000000,
                    "capitalExpenditures": -20000000
                }
            ]
        },
        "incomeStatement": {
            "annualReports": [
                {
                    "fiscalDateEnding": "2023-12-31",
                    "netIncome": 80000000
                }
            ]
        }
    }

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

def test_validate_stock_params():
    """Test input validation for stock valuation endpoint"""
    # Test invalid growth rate
    response = client.get("/api/v1/valuation/AAPL?growth_rate=2.0")
    assert response.status_code == 422

    # Test invalid discount rate
    response = client.get("/api/v1/valuation/AAPL?discount_rate=-0.1")
    assert response.status_code == 422

    # Test invalid terminal method
    response = client.get("/api/v1/valuation/AAPL?terminal_method=invalid")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_stock_valuation():
    """Test stock valuation calculation"""
    with patch('yahoo_finance.YahooFinanceAPI.get_financial_data') as mock_get_data:
        mock_get_data.return_value = mock_financial_data()
        
        response = client.get(
            "/api/v1/valuation/AAPL",
            params={
                "growth_rate": 0.1,
                "discount_rate": 0.1,
                "terminal_method": "gordon",
                "margin_of_safety": 0.3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "intrinsic_value" in data
        assert "margin_of_safety_value" in data
        assert isinstance(data["intrinsic_value"], (int, float))

@pytest.mark.asyncio
async def test_historical_data():
    """Test historical data endpoint"""
    with patch('yahoo_finance.YahooFinanceAPI.get_historical_prices') as mock_get_prices:
        mock_get_prices.return_value = {
            "dates": ["2023-01-01", "2023-01-02"],
            "prices": [150.0, 151.0]
        }
        
        response = client.get("/api/v1/historical-prices/AAPL?period=5d")
        
        assert response.status_code == 200
        data = response.json()
        assert "dates" in data
        assert "prices" in data
        assert len(data["dates"]) == len(data["prices"])

def test_rate_limiter():
    """Test rate limiting functionality"""
    # Make multiple requests quickly
    responses = []
    for _ in range(61):  # Exceed the default 60 requests per minute
        responses.append(client.get("/ping"))
    
    # The last request should be rate limited
    assert responses[-1].status_code == 429
    assert "error" in responses[-1].json()
    assert "rate limit exceeded" in responses[-1].json()["error"].lower()
