# config.py
import os
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    """
    应用全局配置 - 使用 Pydantic 进行类型校验和设置管理
    所有敏感信息都从环境变量或 .env 文件加载
    """
    # --- 环境配置 ---
    # 这里的 ENVIRONMENT 可以是 "development", "testing", "production"
    ENVIRONMENT: Literal["dev", "test", "prod"] = "prod"

    # --- 核心安全配置 ---
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # --- 应用运行配置 ---
    APP_HOST: str = "0.0.0.0"
    # 根据环境自动设置端口
    APP_PORT: int = 8002

    # --- 数据库配置 ---
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    
    # --- 【修正】添加缺失的字段 ---
    #DEV_MYSQL_NAME: str
    #TEST_MYSQL_NAME: str
    #PROD_MYSQL_NAME: str

    DB_NAME: str = "qyxs_dev"  # 默认值，实际值会根据环境动态返回
    
    #@property
    #def DB_NAME(self) -> str:
    #    """计算属性：根据当前的 ENVIRONMENT 动态返回正确的数据库名称。"""
    #    if self.ENVIRONMENT == "development":
    #        return self.DEV_MYSQL_NAME
    #    elif self.ENVIRONMENT == "testing":
    #        return self.TEST_MYSQL_NAME
    #    else: # "production"
    #        return self.PROD_MYSQL_NAME

    @property
    def DATABASE_URI(self) -> str:
        """计算属性：根据其他配置动态拼接出完整的数据库连接 URI。"""
        return (
            f"mysql+asyncmy://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@"
            f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.DB_NAME}"
        )

    # --- 腾讯云与 COS 配置 ---
    COS_BUCKET: str
    TENCENT_SECRET_ID: str
    TENCENT_SECRET_KEY: str
    COS_REGION: str
    COS_BUCKET_NAME: str

    # --- 管理员配置 ---
    ADMIN_OPENID: str

    # --- 微信小程序配置 ---
    WECHAT_APP_ID: str
    WECHAT_APP_SECRET: str
    
    # --- 【修正】添加缺失的字段 ---
    XHS_APP_ID: str
    XHS_APP_SECRET: str

    # --- 微信公众号配置 ---
    WECHAT_MP_APP_ID: str
    WECHAT_MP_APP_SECRET: str

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# 在应用启动时打印出最终确定的模式和数据库 URI，方便调试
print(f"--- 应用运行在 {settings.ENVIRONMENT.upper()} 模式 ---")
print(f"数据库 URI: {settings.DATABASE_URI}")
print(f"使用的 COS 存储桶: {settings.COS_BUCKET}")
print("---------------------------------------------")
