# src/modules/auth/schemas.py

from pydantic import BaseModel

class WxLoginRequest(BaseModel):
    """
    微信登录请求体
    """
    code: str

class TokenResponse(BaseModel):
    """
    返回给客户端的 Token
    """
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """
    JWT Token 中存储的数据
    """
    sub: str  # subject, 存储 user_uid

class AdminLoginRequest(BaseModel):
    """
    管理员 H5 登录请求体
    """
    phone: str
    password: str