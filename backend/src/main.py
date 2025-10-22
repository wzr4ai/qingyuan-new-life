# qingyuan-new-life/backend/src/main.py
from fastapi import FastAPI
from core.lifespan import lifespan
from core.config import settings
from modules.auth import router as auth_router

# 根据不同环境动态设置 API 根路径
api_root_path = ""
if settings.ENVIRONMENT and settings.ENVIRONMENT.lower() != "prod":
    api_root_path = f"/{settings.ENVIRONMENT}"

app = FastAPI(
    title="青元新生 后端服务",
    description="青元新生项目的后端服务，提供API接口支持。",
    version="0.0.1",
    lifespan=lifespan,
    root_path=api_root_path,
    # 仅在非生产环境下启用文档
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

# 添加一个根路径，用于健康检查或欢迎信息
@app.get("/", summary="服务根路径", tags=["Default"])
async def read_root():
    """
    一个简单的根节点，访问 / 时返回欢迎信息。
    可用于检查服务是否正常运行。
    """
    return {"message": "Welcome to the FastAPI backend service!"}

app.include_router(auth_router, prefix="/auth", tags=["认证"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)