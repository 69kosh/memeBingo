from typing import Annotated
from fastapi import APIRouter, Query, Depends
from fastapi.security.http import *
from starlette.status import *
from auth.jwt import checkAccess
from .schemas import *
from .mongoRepo import *


async def getCardsRepo():
	return CardsRepo()


async def getGamesRepo():
	return AbcGamesRepo()


def mustBeSameUser(subject, request):
	return subject.get('userId') == request.get('userId')


router = APIRouter()


@router.get("/cards")
async def listCards(tags: Annotated[list, Query()] = [], limit: int = 20 ,
					cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> list[str]:
	""" Return list of latest cards, filtered by tags"""
	return cardsRepo.findByTags(tags=tags, limit=limit)


@router.get("/cards/tags")
async def listCardsTags(tags: Annotated[list, Query()] = [],
						cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> list[str]:
	""" Aggregate and return a list of popular tags,
		according to already selected ones,
		based on filtered latest cards
	"""
	return cardsRepo.findTagsByTags(tags=tags)


@router.get("/cards/myCards", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def listMyCards(userId: str, cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> list[str]:
	""" Return list of my cards"""
	return cardsRepo.findByAuthor(authorId=userId)


@router.get("/cards/myGames", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def listCardsMyGames(userId: str, gamesRepo: AbcGamesRepo = Depends(getGamesRepo)) -> list[str]:
	""" Return list of cards with my games"""
	return gamesRepo.findCardsByOwner(authorId=userId)


@router.get("/cards/")
async def getCards(ids: Annotated[list, Query()] = [],
				   cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> list[CardView]:
	""" By list of ids return cards"""
	models = cardsRepo.gets(ids=ids)
	return [CardView.parse_obj(model.dict()) for model in models if model is not None]


@router.get("/cards/{id}")
async def getCard(id: str, cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	model = cardsRepo.get(id=id)
	return CardView.parse_obj(model.dict())


@router.post("/cards/", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def createCard(userId: str, card: CardForm,
					 cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	""" Create new card by owner """
	model = CardModel.parse_obj(card.dict() | {'authorId': userId})
	model = cardsRepo.create(card=model)
	return CardView.parse_obj(model.dict())


@router.post("/cards/{id}/clone", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def cloneCard(id: str, userId: str,
					cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	""" Create new card as clone from existed one """
	parentModel = cardsRepo.get(id=id)
	model = CardModel.parse_obj(parentModel.dict(
		exclude=['id', 'createdAt', 'updatedAt', 'authorId', 'parentCardId']) | 
				{'authorId': userId, 'parentCardId': id})
	model = cardsRepo.create(card=model)
	return CardView.parse_obj(model.dict())


@router.put("/cards/{id}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def updateCard(id: str, userId: str, card: CardForm, 
					 cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	""" Update card by owner"""
	model = CardUpdateModel.parse_obj(card.dict())
	model = cardsRepo.update(id, model, conditions={'authorId': userId})
	# check userId == model.authorId
	if model is None:
		raise HTTPException(
			status_code=HTTP_403_FORBIDDEN,
			detail="Not authorized"
		)
	return CardView.parse_obj(model.dict())


@router.delete("/cards/{id}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def hideCard(id: str, userId: str, 
		   cardsRepo: AbcCardsRepo = Depends(getCardsRepo)):
	""" Hide card by owner"""
	success = cardsRepo.hide(id, conditions={'authorId': userId})
	# check userId == model.authorId
	if not success:
		raise HTTPException(
			status_code=HTTP_403_FORBIDDEN,
			detail="Not authorized"
		)


@router.get("/cards/{id}/isOwner/{userId}")
async def isCardOwner(id: str, userId: str, 
		   cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> bool:
	""" Check card owner """
	model = cardsRepo.get(id)
	if model is None:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="Not found"
		)
	return model.authorId == userId


@router.get("/cards/{id}/canShare")
async def canShareCard(id: str) -> bool:
	""" Check card for share, no one was supposed to play the card """
	return True


@router.get("/games/{id}")
async def getGame(id: str) -> GameView:
	return GameView()


@router.get("/games/{id}/canShare")
async def canShareGame(id: str) -> bool:
	return True


@router.post("/games/", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def startGame(userId: str, cardId: str) -> GameView:
	""" Start game by card """
	return GameView()


@router.put("/games/{id}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def updateGame(id: str, userId: str, gameForm: GameForm):
	""" Update game by owner"""
	return GameView()


@router.delete("/games/{id}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def hideGame(id: str, userId: str):
	""" Hide game by owner"""
	...


@router.get("/games/byCard/{cardId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def listMyGamesOfCard(cardId: str, userId: str) -> list[GameView]:
	""" Return list of my games by card"""
	return []
