from pydantic import BaseModel
class UserModel (BaseModel):
	id: str
	name: str
	isGuest: bool = False
	createdAt: int

class AuthModel(BaseModel):
	email: str # unique!
	password: str
	userId: str