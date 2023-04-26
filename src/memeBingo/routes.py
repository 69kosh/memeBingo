from fastapi import APIRouter
from .schemas import *

router = APIRouter()

@router.get("/card")
async def getCard(id: str) -> CardView:
    return CardView()

@router.post("/card")
async def postCard(id: str, card: CardForm) -> CardView:
    return CardView()

@router.get("/")
async def root():
    return {"Hello": "World"}


@router.get("/closed")
async def closed():
    return {"Hello": "Closed"}
