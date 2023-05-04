from pydantic import BaseModel, Field, validator 
import uuid
from datetime import datetime

class UserUpdateModel (BaseModel):
	name: str
	isGuest: bool = False
	createdAt: datetime = Field(default_factory=datetime.utcnow)

class UserModel (UserUpdateModel):
	id: str = Field(default_factory=uuid.uuid4, alias="_id")
	@validator('id', pre=True, always=True)
	def id_to_str(cls, v):
		return str(v)

class AuthUpdateModel(BaseModel):
	password: str
	userId: str

class AuthModel(AuthUpdateModel):
	# грязновато, блин
	_id: str = Field(repr=False)
	email: str
	@validator('email', pre=True, always=True)
	def email_to_id(cls, v, values):
		values['_id'] = v
		return v
