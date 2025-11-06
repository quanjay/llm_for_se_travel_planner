from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # 应用基本配置
    PROJECT_NAME: str = "AI旅行规划师"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        ""
    )
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 通义千问API配置
    QIANWEN_API_KEY: str = os.getenv("QIANWEN_API_KEY", "")
    QIANWEN_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    class Config:
        env_file = ".env"

settings = Settings()