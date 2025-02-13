import motor.motor_asyncio
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class Database:
    _client = None
    _db = None

    @classmethod
    async def _get_db(cls):
        """Get or create database connection"""
        if cls._db is None:
            try:
                # Get MongoDB connection string from environment variable or use default
                mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
                cls._client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
                cls._db = cls._client.stock_valuations
                logger.info("Successfully connected to MongoDB")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise
        return cls._db

    @classmethod
    async def store_valuation(cls, valuation_data: Dict) -> bool:
        """Store a stock valuation result"""
        try:
            db = await cls._get_db()
            collection = db.valuations

            # Add timestamp if not present
            if 'valuation_date' not in valuation_data:
                valuation_data['valuation_date'] = datetime.now().isoformat()

            # Store the valuation
            result = await collection.insert_one(valuation_data)
            logger.info(f"Stored valuation for {valuation_data['ticker']}")
            return bool(result.inserted_id)

        except Exception as e:
            logger.error(f"Error storing valuation: {str(e)}")
            return False

    @classmethod
    async def get_historical_valuations(cls, ticker: str, limit: int = 10) -> List[Dict]:
        """Retrieve historical valuations for a stock"""
        try:
            db = await cls._get_db()
            collection = db.valuations

            # Query the database for historical valuations
            cursor = collection.find(
                {"ticker": ticker},
                {'_id': 0}  # Exclude MongoDB ID
            ).sort('valuation_date', -1).limit(limit)

            valuations = await cursor.to_list(length=limit)
            logger.info(f"Retrieved {len(valuations)} historical valuations for {ticker}")
            return valuations

        except Exception as e:
            logger.error(f"Error retrieving historical valuations: {str(e)}")
            return []

    @classmethod
    async def clear_old_valuations(cls, days: int = 30) -> int:
        """Clear valuations older than specified days"""
        try:
            db = await cls._get_db()
            collection = db.valuations

            cutoff_date = datetime.now() - timedelta(days=days)
            result = await collection.delete_many({
                'valuation_date': {'$lt': cutoff_date.isoformat()}
            })
            
            logger.info(f"Cleared {result.deleted_count} old valuations")
            return result.deleted_count

        except Exception as e:
            logger.error(f"Error clearing old valuations: {str(e)}")
            return 0
