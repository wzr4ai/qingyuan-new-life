# src/core/lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from arq import create_pool
from .worker_settings import ARQ_REDIS_SETTINGS # 导入我们定义好的 Redis 配置

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    管理 arq 连接池的生命周期。
    """
    print("应用启动，正在创建 arq Redis 连接池...")
    
    # 1. 在应用启动时创建连接池
    arq_pool = await create_pool(ARQ_REDIS_SETTINGS)
    # 2. 将连接池存储在 app.state 中，以便路由处理器访问
    app.state.arq_pool = arq_pool
    
    yield  # 应用在此处运行
    
    # 3. 在应用关闭时，优雅地关闭连接池
    print("应用关闭，正在关闭 arq Redis 连接池...")
    await arq_pool.close()