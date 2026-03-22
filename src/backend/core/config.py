from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume NLP Analyzer"
    API_V1_STR: str = "/api"
    
    # Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # Groq API
    GROQ_API_KEY: Optional[str] = None

    # Hugging Face
    HUGGINGFACE_HUB_TOKEN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
