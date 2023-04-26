from pydantic import BaseModel

class UserAttributes(BaseModel):
    id: str | None
    isGuest: bool | None
    name: str | None

class LoginForm(BaseModel):
    email: str
    password: str

class SignupForm(BaseModel):
    name: str
    email: str
    password: str

class SignupFormResponse(BaseModel):
	userId: str