import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # Project paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    SRC_DIR = BASE_DIR / "src"
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Configuration
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
    
    # Application Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
    MAX_SEARCH_RADIUS_KM = float(os.getenv("MAX_SEARCH_RADIUS_KM", "5"))
    
    # Agent Configuration
    TEMPERATURE = 0.7
    MAX_TOKENS = 1024
    TOP_P = 0.95
    
    # RAG Configuration
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 3
    
    # Vector Store
    VECTORSTORE_PATH = DATA_DIR / "vectorstore"
    FAISS_INDEX_NAME = "customer_support_index"
    
    # Data Files
    CUSTOMERS_FILE = DATA_DIR / "customers.json"
    LOCATIONS_FILE = DATA_DIR / "locations.json"
    PRODUCTS_FILE = DATA_DIR / "products.json"
    PROMOTIONS_FILE = DATA_DIR / "promotions.json"
    POLICIES_FILE = DATA_DIR / "policies.json"
    FAQS_FILE = DATA_DIR / "faqs.json"
    
    # Privacy Settings
    ENABLE_PII_MASKING = True
    PII_ENTITIES = ["PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "IP_ADDRESS"]
    
    # Location Settings
    DEFAULT_LOCATION = {
        "latitude": 28.6139,  # Delhi, India
        "longitude": 77.2090,
        "city": "Delhi",
        "country": "India"
    }
    
    # Business Hours
    BUSINESS_HOURS = {
        "monday": "09:00-21:00",
        "tuesday": "09:00-21:00",
        "wednesday": "09:00-21:00",
        "thursday": "09:00-21:00",
        "friday": "09:00-22:00",
        "saturday": "09:00-22:00",
        "sunday": "10:00-20:00"
    }
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        errors = []
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set in .env file")
        
        # Create data directory if it doesn't exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.VECTORSTORE_PATH.mkdir(exist_ok=True)
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def get_info(cls):
        """Get configuration info (safe for logging)"""
        return {
            "model": cls.GEMINI_MODEL,
            "embedding_model": cls.EMBEDDING_MODEL,
            "debug_mode": cls.DEBUG_MODE,
            "max_search_radius": cls.MAX_SEARCH_RADIUS_KM,
            "pii_masking": cls.ENABLE_PII_MASKING,
            "api_key_set": bool(cls.GOOGLE_API_KEY)
        }


# Global settings instance
settings = Settings()

# Validate on import
if settings.GOOGLE_API_KEY:  # Only validate if key is set
    try:
        settings.validate()
    except ValueError as e:
        print(f"Warning: {e}")