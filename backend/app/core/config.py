from pydantic import BaseModel
from typing import List
import os
from pathlib import Path


class Settings(BaseModel):
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME: str = "智能出行应用"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # 和风天气API配置
    HEFENG_API_KEY: str = ""
    HEFENG_BASE_URL: str = "https://devapi.qweather.com"
    
    # 高德地图API配置
    AMAP_API_KEY: str = ""
    AMAP_SECURITY_KEY: str = ""
    AMAP_BASE_URL: str = "https://restapi.amap.com"
    
    # 请求超时配置
    REQUEST_TIMEOUT: int = 30
    
    # 缓存配置
    CACHE_EXPIRE_SECONDS: int = 300  # 5分钟
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局设置实例，从环境变量读取配置
settings = Settings(
    HEFENG_API_KEY=os.getenv("HEFENG_API_KEY", ""),
    AMAP_API_KEY=os.getenv("AMAP_API_KEY", ""),
    AMAP_SECURITY_KEY=os.getenv("AMAP_SECURITY_KEY", ""),
    DEBUG=os.getenv("DEBUG", "True").lower() == "true",
    HOST=os.getenv("HOST", "0.0.0.0"),
    PORT=int(os.getenv("PORT", "8000"))
)


# 验证必要的API密钥
def validate_api_keys():
    """验证API密钥是否配置"""
    missing_keys = []
    
    if not settings.HEFENG_API_KEY:
        missing_keys.append("HEFENG_API_KEY")
    
    if not settings.AMAP_API_KEY:
        missing_keys.append("AMAP_API_KEY")
    
    if missing_keys:
        print(f"⚠️  警告: 以下API密钥未配置: {', '.join(missing_keys)}")
        print("请在.env文件中配置相应的API密钥")
    
    return len(missing_keys) == 0


# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent