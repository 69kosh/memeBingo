from pydantic import BaseModel
from datetime import datetime

class CardForm(BaseModel):
    phrases: list[str]
    title: str 
    description: str
    tags: list[str]
    outlineColor: str
    textColor: str
    backgroundColor: str
    markType: str

class CardView(CardForm):
    id: str
    authorId: str
    createdAt: datetime
    updatedAt: datetime


class GameForm(BaseModel):
    checkedPhrases: list[int]
    markType: str

class GameView(GameForm):
    id: str
    cardId: str
    ownerId: str
    createdAt: datetime
    updatedAt: datetime

