# src/modules/auth/service.py

import httpx
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload # <-- 1. 导入 joinedload
from sqlalchemy.exc import IntegrityError # <-- 2. 导入 IntegrityError
from jose import jwt, JWTError

from src.core.config import settings
# 3. 导入两个模型
from src.shared.models.user_models import User, SocialAccount 
from .schemas import TokenPayload

# --- 微信 API (exchange_code_for_session 函数保持不变) ---
WECHAT_SESSION_API = "https://api.weixin.qq.com/sns/jscode2session"
WX_LOGIN_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="微信登录失败，请重试"
)

async def exchange_code_for_session(code: str) -> dict:
    """
    使用 code 换取微信 openid 和 session_key
    """
    params = {
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(WECHAT_SESSION_API, params=params)
            response.raise_for_status() 
            data = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"请求微信 API 失败: {e}")
            raise WX_LOGIN_ERROR

    if data.get("errcode", 0) != 0:
        print(f"微信 API 返回错误: {data}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=data.get("errmsg", "微信登录凭证无效")
        )
    
    return data

# --- 4. 替换为新的 V3 核心逻辑 ---

async def get_or_create_user_by_social(
    db: AsyncSession, 
    provider: str, 
    provider_id: str
) -> User:
    """
    V3: 根据社交账号查找或创建用户
    """
    
    # 1. 尝试查找 SocialAccount，并同时加载 (eager load) 关联的 User
    query = (
        select(SocialAccount)
        .where(
            SocialAccount.provider == provider,
            SocialAccount.provider_id == provider_id
        )
        .options(joinedload(SocialAccount.user)) # 关键优化：避免 N+1 查询
    )
    result = await db.execute(query)
    social_account = result.scalars().first()
    
    if social_account:
        return social_account.user  # 老用户，直接返回

    # 2. 新用户：在事务中创建 User 和 SocialAccount
    try:
        # 创建 User (此时 nickname="微信用户", phone=None)
        new_user = User()
        db.add(new_user)
        await db.flush()  # 立即执行插入，以便获取 new_user.uid

        # 创建 SocialAccount 并关联
        new_social = SocialAccount(
            user_id=new_user.uid,
            provider=provider,
            provider_id=provider_id
        )
        db.add(new_social)
        
        await db.commit()
        await db.refresh(new_user) # 刷新 new_user 以获取所有数据
        
        return new_user

    except IntegrityError:
        # 极小概率下，两个请求同时尝试创建同一个(provider, provider_id)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户时发生并发冲突，请重试"
        )
    except Exception as e:
        await db.rollback()
        print(f"创建用户和社交账号失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户时发生错误"
        )


# --- JWT Token (create_access_token 函数保持不变) ---
JWT_SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject), 
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt