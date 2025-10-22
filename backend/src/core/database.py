# src/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .config import settings

# 1. 创建数据库连接 URL
# 格式: "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URI

# 2. 创建 SQLAlchemy 引擎 (Engine)
# 'engine' 是 SQLAlchemy 应用的核心接口，负责与数据库建立连接。
# connect_args 是只为 SQLite 需要的。对于其他数据库，你不需要它。
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False} # 仅在_sqlite_时需要
)

# 3. 创建数据库会话工厂 (SessionLocal)
# 每个 SessionLocal 的实例都将是一个数据库会话。
# autocommit=False 和 autoflush=False 是为了让你能手动控制事务。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 创建一个声明基类 (Base)
# 之后我们创建的所有数据库模型（ORM models）都将继承这个类。
Base = declarative_base()


# 5. 创建一个可复用的依赖项 (Dependency)
def get_db():
    """
    一个 FastAPI 依赖项，它为每个请求创建一个新的 SQLAlchemy 会话，
    并在请求完成后关闭它。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()