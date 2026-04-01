from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from pydantic import ConfigDict


# What we accept when CREATING a user
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# What we accept when UPDATING a user (all fields optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


# What we RETURN to the client (never expose password!)
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    # class Config:
    #     from_attributes = True  # allows ORM objects later


model_config = ConfigDict(from_attributes=True)
