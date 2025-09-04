from pydantic_settings import BaseSettings

class Settings(BaseSettings):
   
    DB_NAME: str
    USER_NAME: str
    DB_PASSCODE: str
    DB_HOST: str
    DB_PORT: str
   
    API_URL: str
    
   
    SECRET_KEY: str = "Exynos850"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"
        case_sensitive = False  

settings = Settings()