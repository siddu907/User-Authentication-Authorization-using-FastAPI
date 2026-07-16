from datetime import datetime
from typing import Optional
from pydantic import BaseModel,ConfigDict,EmailStr,Field

# User Registration
class UserCreate(BaseModel):

    full_name: str = Field(...,min_length=3,max_length=100)
    email: EmailStr = Field(...)
    password: str = Field(...,min_length=8,max_length=100,examples=["StrongPassword123"])

# User Login

class UserLogin(BaseModel):

    email: EmailStr = Field(...)
    password: str = Field(...,examples=["StrongPassword123"])

# User Response

class UserResponse(BaseModel):

    id: int

    full_name: str

    email: EmailStr

    created_at: datetime

    verification_token: Optional[str] = None

    message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# JWT TOKEN SCHEMAS

class Token(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str

    message: Optional[str] = None


class TokenData(BaseModel):

    user_id: Optional[int] = None

    email: Optional[EmailStr] = None

    role: Optional[str] = None

# EMAIL VERIFICATION

class VerifyEmail(BaseModel):

    token: str

# FORGOT PASSWORD

class ForgotPassword(BaseModel):

    email: EmailStr


class ResetPassword(BaseModel):

    token: str

    new_password: str = Field(...,min_length=8,max_length=100)

# Create Task

class TaskCreate(BaseModel):

    title: str = Field(...,min_length=3,max_length=150)
    description: str = Field(...,min_length=5,max_length=500)
    status: str = Field(default="Pending")

# Update Task

class TaskUpdate(BaseModel):

    title: Optional[str] = Field(default=None,min_length=3,max_length=150)
    description: Optional[str] = Field(default=None,min_length=5,max_length=500)
    status: Optional[str] = Field(default=None)

# Task Response

class TaskResponse(BaseModel):

    id: int

    title: str

    description: str

    status: str

    user_id: int

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):

    id: int

    full_name: str

    email: EmailStr

    created_at: datetime

    tasks: list[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)


class UserDeleteResponse(BaseModel):

    message: str


class TaskDeleteResponse(BaseModel):

    message: str


# Pagination Response

class PaginatedTasks(BaseModel):

    total_records: int

    current_page: int

    page_size: int

    data: list[TaskResponse]