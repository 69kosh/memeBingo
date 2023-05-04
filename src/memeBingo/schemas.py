from pydantic import BaseModel

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
    createdAt: int
    updatedAt: int


class GameForm(BaseModel):
    checkedPhrases: list[int]
    markType: str

class GameView(GameForm):
    id: str
    cardId: str
    ownerId: str

