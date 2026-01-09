from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Keys
    GROQ_API_KEY: str
    GEMINI_API_KEY: str

    # Blockchain
    BLOCKCHAIN_RPC_URL: str = "http://127.0.0.1:7545"
    BLOCKCHAIN_PRIVATE_KEY: str
    CONTRACT_ADDRESS: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()