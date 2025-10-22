from pydantic import BaseModel, EmailStr
from typing import Optional
class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

