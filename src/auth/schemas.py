from pydantic import BaseModel, EmailStr, Field

class UserAttributes(BaseModel):
    id: str | None
    isGuest: bool | None
    name: str | None

class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class SignupForm(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)
