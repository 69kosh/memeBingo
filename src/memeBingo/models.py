from pydantic import BaseModel, Field, validator 
import uuid
from datetime import datetime

class CardUpdateModel(BaseModel):
	phrases: list[str]
	title: str 
	description: str
	tags: list[str]
	outlineColor: str
	textColor: str
	backgroundColor: str
	markType: str
	updatedAt: datetime = Field(default_factory=datetime.utcnow)

class CardModel(CardUpdateModel):
	id: str = Field(default_factory=uuid.uuid4, alias="_id")
	authorId: str
	parentCardId: str | None
	createdAt: datetime = Field(default_factory=datetime.utcnow)
	hidden: bool = False

	@validator('id', pre=True, always=True)
	def id_to_str(cls, v):
		return str(v)

class GameUpdateModel(BaseModel):
	checkedPhrases: list[int] = Field(default=[])
	markType: str
	updatedAt: datetime = Field(default_factory=datetime.utcnow)

class GameModel(GameUpdateModel):
	id: str = Field(default_factory=uuid.uuid4, alias="_id")
	cardId: str
	ownerId: str
	createdAt: datetime = Field(default_factory=datetime.utcnow)
	hidden: bool = False

	@validator('id', pre=True, always=True)
	def id_to_str(cls, v):
		return str(v)
