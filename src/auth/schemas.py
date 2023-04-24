from pydantic import BaseModel

class UserFeatures(BaseModel):
    id: str | None
    isGuest: bool = False
    name: str | None

class LoginForm(BaseModel):
    email: str
    password: str

class SingupForm(BaseModel):
    name: str
    email: str
    password: str

class SingupFormResponse(BaseModel):
	userId: str