from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str = "dev-secret" 
    LLM_API_KEY: str = ""         
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"

    model_config = SettingsConfigDict(
        env_file=".env",   
        extra="ignore",    
    )

settings = Settings()