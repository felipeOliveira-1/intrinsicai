from yahoo_finance import YahooFinanceAPI
import logging

logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self):
        self.yahoo = YahooFinanceAPI()
        
    async def analyze_stock(self, ticker: str) -> dict:
        """
        Analyze if a stock is a good buy based on its intrinsic value.
        Returns a simple recommendation with the analysis.
        """
        try:
            # Get financial data
            data = await self.yahoo.get_financials(ticker)
            
            # Get the most recent free cash flow
            fcf = list(data['cash_flow']['free_cashflow'].values())[0]
            shares = data['market_data']['shares_outstanding']
            current_price = data['market_data']['current_price']
            
            # Calculate FCF per share
            fcf_per_share = fcf / shares
            
            # Simple valuation using 10x multiple
            fair_value = fcf_per_share * 10
            
            # Calculate margin of safety (30%)
            buy_price = fair_value * 0.7
            
            # Determine if it's a good buy
            is_good_buy = current_price <= buy_price
            upside_potential = ((fair_value - current_price) / current_price) * 100
            
            return {
                'ticker': ticker,
                'recommendation': 'BUY' if is_good_buy else 'HOLD',
                'current_price': round(current_price, 2),
                'fair_value': round(fair_value, 2),
                'buy_below': round(buy_price, 2),
                'upside_potential': round(upside_potential, 2),
                'analysis': {
                    'fcf_per_share': round(fcf_per_share, 2),
                    'shares_outstanding': shares,
                    'total_fcf': fcf
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stock {ticker}: {str(e)}")
            raise Exception(f"Failed to analyze stock: {str(e)}")
