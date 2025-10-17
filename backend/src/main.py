# qingyuan-new-life/backend/src/main.py
from fastapi import FastAPI
from src.core.config import settings

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "欢迎来到清缘新生活"}

@app.get("/hello")
def read_hello():
    return {"message": "你好，世界"}

#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)