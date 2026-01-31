import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", "0")) 
    API_HASH = os.getenv("API_HASH", "")
    SESSION = os.getenv("SESSION", "")
    
    # Handlers (Prefixes)
    HANDLER = [".", "!"]
    
    # Database
    MONGO_URI = os.getenv("MONGO_URI", None) 
    REDIS_URI = os.getenv("REDIS_URI", None)
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

    # --- NEW: Sudo & Updates ---
    # Add User IDs of friends you trust (separated by spaces in .env)
    # e.g. SUDO_USERS=123456789 987654321
    SUDO_USERS = [int(x) for x in os.getenv("SUDO_USERS", "").split()] if os.getenv("SUDO_USERS") else []
    
    # For the .update command
    UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "")