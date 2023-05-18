from pydantic import BaseModel, Field
from datetime import datetime

class CardForm(BaseModel):
    phrases: list[str]
    title: str 
    description: str
    tags: list[str] = Field(default = [])
    appearance: dict = Field(default = {})

class CardView(CardForm):
    id: str
    authorId: str
    createdAt: datetime
    updatedAt: datetime
    parentCardId: str | None
    hidden: bool = False


class GameForm(BaseModel):
    checkedPhrases: list[int] = Field(default = [])

class GameView(GameForm):
    id: str
    cardId: str
    ownerId: str
    createdAt: datetime
    updatedAt: datetime
    hidden: bool = False

