from pydantic import BaseModel, Field, validator 
import uuid
from datetime import datetime

def now(): 
	# Milliseconds Precision couse mongo :(
	return datetime.utcfromtimestamp(int(datetime.utcnow().timestamp() * 1000 ) / 1000)

class CardUpdateModel(BaseModel):
	phrases: list[str]
	title: str 
	description: str
	tags: list[str]
	# outlineColor: str
	# textColor: str
	# backgroundColor: str
	# markType: str
	appearance: dict = Field(default = {})
	updatedAt: datetime = Field(default_factory=now)

class CardSetIsGuestModel(BaseModel):
	isGuest: bool
	updatedAt: datetime = Field(default_factory=now)

class CardModel(CardUpdateModel):
	id: str = Field(default_factory=uuid.uuid4, alias="_id")
	authorId: str
	parentCardId: str | None
	createdAt: datetime = Field(default_factory=now)
	hidden: bool = False
	isGuest: bool = True

	@validator('id', pre=True, always=True)
	def id_to_str(cls, v):
		return str(v)

class GameUpdateModel(BaseModel):
	checkedPhrases: list[int] = Field(default=[])
	# markType: str | None
	updatedAt: datetime = Field(default_factory=now) 

class GameSetIsGuestModel(BaseModel):
	isGuest: bool
	updatedAt: datetime = Field(default_factory=now)

class GameModel(GameUpdateModel):
	id: str = Field(default_factory=uuid.uuid4, alias="_id")
	cardId: str
	ownerId: str
	createdAt: datetime = Field(default_factory=now) 
	hidden: bool = False
	isGuest: bool = True
	
	@validator('id', pre=True, always=True)
	def id_to_str(cls, v):
		return str(v)
