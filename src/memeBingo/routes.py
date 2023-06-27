from typing import Annotated
from fastapi import APIRouter, Query, Depends
from starlette.responses import StreamingResponse
from fastapi.security.http import *
from typing import Literal
from starlette.status import *
from auth.jwt import checkAccess
from .schemas import *
from .mongoRepo import *
from interchange import getUsersRepo, AbcUsersRepo
from .imagesGenerator import ImagesGenerator

from pymongo import MongoClient
from dotenv import load_dotenv
import os
from io import BytesIO
from os import getcwd

basePath = getcwd()

load_dotenv()
PASSWORD_SALT = os.getenv('PASSWORD_SALT')
MONGODB_URL = os.getenv('MONGODB_URL')
mongoClient = MongoClient(MONGODB_URL, uuidRepresentation='standard')
mongoDb = mongoClient.get_database('meme')
cardsCollection = mongoDb.get_collection('cards')
gamesCollection = mongoDb.get_collection('games')


async def getCardsRepo():
	return CardsRepo(cardsCollection)

async def getGamesRepo():
	return GamesRepo(gamesCollection)

async def getImagesGenerator():
	# print('Awaiting font file: ' + basePath + "/assets/Roboto-Regular.ttf")
	return ImagesGenerator(assetsDir=basePath + "/assets/")

def mustBeSameUser(subject, request):
	return subject.get('userId') == request.get('userId') if request.get('userId') is not None else False


router = APIRouter()

@router.get("/cards")
async def listCards(tags: Annotated[list, Query()] = [], limit: int = 20,
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
async def listCardsMyGames(userId: str, cardsRepo: AbcCardsRepo = Depends(getCardsRepo), 
			   gamesRepo: AbcGamesRepo = Depends(getGamesRepo)) -> list[str]:
	""" Return list of cards with my games"""
	ids = gamesRepo.findCardsByOwner(ownerId=userId)
	return cardsRepo.filterCardsByHidden(ids)


@router.get("/cards/")
async def getCards(ids: Annotated[list, Query()] = [],
				   cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> list[CardView]:
	""" By list of ids return cards"""
	models = cardsRepo.gets(ids=ids)
	return [CardView.parse_obj(model.dict()) for model in models if model is not None]


@router.get("/cards/{id}")
async def getCard(id: str, cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	model = cardsRepo.get(id)
	if model is None:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="Not found"
		)
	return CardView.parse_obj(model.dict())

# @router.get("/cards/{id}/canView")
# async def canCardView(id: str, cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> bool:
# 	''' Check if card not hide and author of card is not guest or author is current user'''
# 	model = cardsRepo.get(id)
# 	if model is None:
# 		raise HTTPException(
# 			status_code=HTTP_404_NOT_FOUND,
# 			detail="Not found"
# 		)
# 	return CardView.parse_obj(model.dict())


@router.post("/cards/", status_code=201, dependencies=[Depends(checkAccess(mustBeSameUser))])
async def createCard(userId: str, card: CardForm,
					 cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	""" Create new card by owner """
	model = CardModel.parse_obj(card.dict() | {'authorId': userId})
	id = cardsRepo.create(card=model)
	return CardView.parse_obj(model.dict())


@router.post("/cards/{id}/clone", status_code=201, dependencies=[Depends(checkAccess(mustBeSameUser))])
async def cloneCard(id: str, userId: str,
					cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	""" Create new card as clone from existed one """
	parentModel = cardsRepo.get(id=id)
	newModel = parentModel.dict(exclude=set(['id', 'createdAt', 'updatedAt', 'authorId', 'parentCardId'
											 ])) | {'authorId': userId, 'parentCardId': id}
	model = CardModel.parse_obj(newModel)
	id = cardsRepo.create(card=model)
	return CardView.parse_obj(model.dict())


@router.put("/cards/{id}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def updateCard(id: str, userId: str, card: CardForm,
					 cardsRepo: AbcCardsRepo = Depends(getCardsRepo)) -> CardView:
	""" Update card by owner"""
	model = CardUpdateModel.parse_obj(card.dict())
	# check userId == model.authorId
	success = cardsRepo.update(id, model, conditions={'authorId': userId})
	if not success:
		raise HTTPException(
			status_code=HTTP_403_FORBIDDEN,
			detail="Not authorized"
		)
	model = cardsRepo.get(id=id)
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
async def canShareCard(id: str, cardsRepo: AbcCardsRepo = Depends(getCardsRepo), 
		       usersRepo: AbcUsersRepo = Depends(getUsersRepo)) -> bool:
	""" Check card for share, the card author must not be a guest and card not hidden"""
	try:
		card = cardsRepo.get(id)
		user = usersRepo.get(card.authorId)
		return not user.isGuest and not card.hidden
	except:
		return False
	

@router.get("/games/{id}/canShare")
async def canShareGame(id: str, gamesRepo: AbcGamesRepo = Depends(getGamesRepo),
		       cardsRepo: AbcCardsRepo = Depends(getCardsRepo), 
		       usersRepo: AbcUsersRepo = Depends(getUsersRepo)) -> bool:
	""" Check game for share, the card author must not be a guest, game owner must not be a guest and card and game not hidden"""
	try:
		game = gamesRepo.get(id)
		card = cardsRepo.get(game.cardId)
		author = usersRepo.get(card.authorId)
		owner = usersRepo.get(game.ownerId)
		return not author.isGuest and not owner.isGuest and not card.hidden and not game.hidden
	except:
		return False
	

@router.get("/cards/{id}/canEdit")
async def canEditCard(id: str, gamesRepo: AbcGamesRepo = Depends(getGamesRepo)) -> bool:
	""" Check card for edit, it must not be played """
	return gamesRepo.getCountByCard(id) == 0

@router.get("/games/{id}")
async def getGame(id: str, gamesRepo: AbcGamesRepo = Depends(getGamesRepo)) -> GameView:
	model = gamesRepo.get(id)
	if model is None:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="Not found"
		)
	return GameView.parse_obj(model.dict())


@router.post("/games/", status_code=201, dependencies=[Depends(checkAccess(mustBeSameUser))])
async def startGame(userId: str, cardId: str,
					cardsRepo: AbcCardsRepo = Depends(getCardsRepo),
					gamesRepo: AbcGamesRepo = Depends(getGamesRepo)) -> GameView:
	""" Start game by card """
	card = cardsRepo.get(cardId)
	model = GameModel(ownerId=userId, cardId=cardId)
	gameId = gamesRepo.create(game=model)
	return GameView.parse_obj(model.dict())


@router.put("/games/{id}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def updateGame(id: str, userId: str, gameForm: GameForm,
					 gamesRepo: AbcGamesRepo = Depends(getGamesRepo)):
	""" Update game by owner"""
	model = GameUpdateModel.parse_obj(gameForm.dict())
	success = gamesRepo.update(id, model, conditions={'ownerId': userId})
	# check userId == model.ownerId
	if not success:
		raise HTTPException(
			status_code=HTTP_403_FORBIDDEN,
			detail="Not authorized"
		)
	model = gamesRepo.get(id)  # а надо ли оно?
	return GameView.parse_obj(model.dict())


@router.delete("/games/{id}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def hideGame(id: str, userId: str, gamesRepo: AbcGamesRepo = Depends(getGamesRepo)):
	""" Hide game by owner"""
	success = gamesRepo.hide(id, conditions={'ownerId': userId})
	# check userId == model.authorId
	if not success:
		raise HTTPException(
			status_code=HTTP_403_FORBIDDEN,
			detail="Not authorized"
		)


@router.get("/games/byCard/{cardId}", dependencies=[Depends(checkAccess(mustBeSameUser))])
async def listMyGamesOfCard(cardId: str, userId: str,
							gamesRepo: AbcGamesRepo = Depends(getGamesRepo)) -> list[GameView]:
	""" Return list of my games by card"""
	models = gamesRepo.getMyGamesByCard(cardId=cardId, ownerId=userId)
	return [GameView.parse_obj(model.dict()) for model in models if model is not None]


@router.get("/cards/{id}/image-{withTitle}-{size}.{type}")
async def getCardImage(id: str, size: Literal['full', 'small'] = 'full', 
		       withTitle: Literal['untitled', 'titled'] = 'untitled', type: Literal['png', 'jpeg'] = 'png', 
			   cardsRepo: AbcCardsRepo = Depends(getCardsRepo),
			   imagesGenerator: ImagesGenerator = Depends(getImagesGenerator)) -> StreamingResponse:
	card = cardsRepo.get(id)
	if card is None:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
		)
	
	image = imagesGenerator.getCardImage(card = card, size = size, withTitle = withTitle == 'titled')

	bytes = BytesIO()
	image = image.convert('RGB')
	image.save(bytes, type)
	bytes.seek(0)

	return StreamingResponse(bytes, media_type="image/" + type)


@router.get("/games/{id}/image-{withTitle}-{size}.{type}")
async def getGameImage(id: str, size: Literal['full', 'small'] = 'full', 
		       withTitle: Literal['untitled', 'titled'] = 'untitled', type: Literal['png', 'jpeg'] = 'png', 
		  cardsRepo: AbcCardsRepo = Depends(getCardsRepo), gamesRepo: AbcGamesRepo = Depends(getGamesRepo),
		  imagesGenerator: ImagesGenerator = Depends(getImagesGenerator)) -> StreamingResponse:
	

	game = gamesRepo.get(id)
	if game is None:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
		)

	card = cardsRepo.get(game.cardId)
	if card is None:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
		)
	
	image = imagesGenerator.getGameImage(card = card, game = game, size = size, withTitle = withTitle == 'titled')

	bytes = BytesIO()
	image = image.convert('RGB')
	image.save(bytes, type)
	bytes.seek(0)

	return StreamingResponse(bytes, media_type="image/" + type)
