# src/core/worker_settings.py
from arq.connections import RedisSettings
from .config import settings

# 1. 在这里导入你的任务函数
from modules.auth.tasks import send_welcome_email_task

# 2. 定义 Redis 连接
ARQ_REDIS_SETTINGS = RedisSettings.from_dsn(settings.REDIS_URL)

# 3. 定义 Worker 设置类
class WorkerSettings:
    """
    arq worker 启动时加载的主配置。
    """
    # 4. 把导入的函数对象放到这个列表里，arq 就知道它是一个任务了
    functions = [
        send_welcome_email_task,
        # 如果有其他任务，继续在这里添加
    ]
    
    # 5. 关联 Redis 配置
    redis_settings = ARQ_REDIS_SETTINGS
    
    # 6. (可选) 添加文档中的启动/关闭钩子
    # on_startup = startup_function
    # on_shutdown = shutdown_function