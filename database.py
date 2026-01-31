import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from config import Config

class Database:
    def __init__(self):
        self.mongo_client = None
        self.mongo_db = None
        self.redis_client = None

    async def connect(self):
        print("--- Connecting to Databases ---")
        
        # 1. Connect to MongoDB
        if Config.MONGO_URI:
            try:
                self.mongo_client = AsyncIOMotorClient(Config.MONGO_URI)
                # Helper to check connection
                await self.mongo_client.admin.command('ping')
                self.mongo_db = self.mongo_client.ultroid_pyro  # Database Name
                print("✅ MongoDB Connected")
            except Exception as e:
                print(f"❌ MongoDB Failed: {e}")
        else:
            print("⚠️ No MONGO_URI found. MongoDB is disabled.")

        # 2. Connect to Redis
        if Config.REDIS_URI:
            try:
                # Format: redis://host:port or just host
                self.redis_client = Redis.from_url(
                    Config.REDIS_URI,
                    password=Config.REDIS_PASSWORD,
                    decode_responses=True # Returns strings instead of bytes
                )
                await self.redis_client.ping()
                print("✅ Redis Connected")
            except Exception as e:
                print(f"❌ Redis Failed: {e}")
        else:
            print("⚠️ No REDIS_URI found. Redis is disabled.")

    # --- Helper Functions (Abstraction) ---
    
    async def set_key(self, key, value):
        """Sets a key in Redis (fast) or Mongo (fallback)"""
        if self.redis_client:
            return await self.redis_client.set(key, value)
        elif self.mongo_db is not None:
            # Upsert into a 'cache' collection
            await self.mongo_db.cache.update_one(
                {"_id": key}, {"$set": {"value": value}}, upsert=True
            )
            return True
        return False

    async def get_key(self, key):
        """Gets a key from Redis or Mongo"""
        if self.redis_client:
            return await self.redis_client.get(key)
        elif self.mongo_db is not None:
            doc = await self.mongo_db.cache.find_one({"_id": key})
            return doc["value"] if doc else None
        return None

    async def del_key(self, key):
        if self.redis_client:
            return await self.redis_client.delete(key)
        elif self.mongo_db is not None:
            return await self.mongo_db.cache.delete_one({"_id": key})
        return None

# Create a global instance
db = Database()