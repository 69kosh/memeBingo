from pydantic import BaseModel

class CardView(BaseModel):
    id: str
    authorId: str
    phrases: list[str]
    title: str 
    description: str
    tags: list[str]
    outlineColor: str
    textColor: str
    backgroundColor: str
    markType: str
    created: int
    updated: int
    
class CardForm(BaseModel):
    # id: str
    # authorId: str
    phrases: list[str]
    title: str 
    description: str
    tags: list[str]
    outlineColor: str
    textColor: str
    backgroundColor: str
    markType: str

