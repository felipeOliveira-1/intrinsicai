from yahoo_fin import stock_info as si
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_yahoo_fin():
    ticker = "INTC"
    try:
        # Test cash flow data
        logger.info("Testing cash flow data...")
        cash_flow = si.get_cash_flow(ticker)
        logger.info(f"Cash flow data shape: {cash_flow.shape}")
        logger.info(f"Cash flow index: {cash_flow.index.tolist()}")
        logger.info(f"Cash flow columns: {cash_flow.columns.tolist()}")
        logger.info("\nFirst few rows of cash flow:")
        logger.info(cash_flow.head())

        # Test stats data
        logger.info("\nTesting stats data...")
        stats = si.get_stats(ticker)
        logger.info(f"Stats data shape: {stats.shape}")
        logger.info(f"Stats columns: {stats.columns.tolist()}")
        logger.info("\nStats data:")
        logger.info(stats)

        # Test live price
        logger.info("\nTesting live price...")
        price = si.get_live_price(ticker)
        logger.info(f"Current price: {price}")

    except Exception as e:
        logger.error(f"Error testing yahoo_fin: {str(e)}")
        raise

if __name__ == "__main__":
    test_yahoo_fin()
