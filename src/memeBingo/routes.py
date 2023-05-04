from typing import Annotated
from fastapi import APIRouter, Query, Depends
from auth.jwt import checkAccess, mustBeAuthorized
from .schemas import *

def mustBeSameUser(subject, request):
    return subject.get('userId') == request.get('userId')

router = APIRouter()

@router.get("/cards")
async def listCards(tags: Annotated[list, Query()] = [], limit:int = 20) -> list[str]:
    """ Return list of latest cards, filtered by tags"""
    return []

@router.get("/cards/tags")
async def listCardsTags(tags: Annotated[list, Query()] = []) -> list[str]:
    """ Aggregate and return a list of popular tags, according to already selected ones, based on filtered latest cards"""    
    return []

@router.get("/cards/my/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def listMyCards(userId: str) -> list[str]:
    """ Return list of my cards"""
    return []

@router.get("/cards/myGames/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def listCardsMyGames(userId: str) -> list[str]:
    """ Return list of cards with my games"""
    return []

@router.get("/cards/")
async def getCards(ids: Annotated[list, Query()] = []) -> list[CardView]:
    """ By list of ids return cards"""
    return [CardView()]

@router.get("/cards/{id}")
async def getCard(id: str) -> CardView:
    return CardView()

@router.post("/cards/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def createCard(userId: str, card: CardForm) -> CardView:
    """ Create new card by owner """
    return CardView()

@router.put("/cards/{id}/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def updateCard(id: str, userId: str, card: CardForm) -> CardView:
    """ Update card by owner"""
    return CardView()

@router.delete("/cards/{id}/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def hideCard(id: str, userId: str):
    """ Hide card by owner"""
    ...

@router.get("/cards/{id}/isOwner/{userId}")
async def isCardOwner(id: str, userId: str) -> bool:
    """ Check card owner """
    return True

@router.get("/cards/{id}/canShare")
async def canShareCard(id: str) -> bool:
    """ Check card for chare """
    return True

@router.post("/cards/{id}/clone/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def cloneCard(id: str, userId: str, card: CardForm) -> CardView:
    """ Create new card as clone from existed one """
    return CardView()

@router.post("/games/{userId}/{cardId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def startGame(cardId: str, userId: str) -> GameView:
    """ Start game by card """
    return GameView()

@router.get("/games/{id}")
async def getGame(id: str) -> GameView:
    return GameView()

@router.get("/games/{id}/canShare")
async def canShareGame(id: str) -> bool:
    return True

@router.put("/games/{id}/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def updateGame(id: str, userId: str, gameForm: GameForm):
    """ Update game by owner"""
    return GameView()

@router.delete("/games/{id}/{userId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def hideGame(id: str, userId: str):
    """ Hide game by owner"""
    ...

@router.get("/games/my/{userId}/{cardId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def listMyGamesOfCard(userId: str, cardId: str) -> list[GameView]:
    """ Return list of my games by card"""
    return []

# updateGame({
# Id: ID
# 	checked: int[]
# markType: string
# })

# findCardsOfMyGames(userId)
# ??? getCards(ids:ID[])
# getMyGamesOfCard(cardId, userId)
