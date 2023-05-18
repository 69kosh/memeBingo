from fastapi.testclient import TestClient
from memeBingo.routes import router as memeRouter, getCardsRepo, getGamesRepo
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from memeBingo.repo import *
from memeBingo.mongoRepo import CardsRepo, GamesRepo
from pymongo import MongoClient
from exceptions import OtherValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from auth.jwt import signToken

import re

app = FastAPI(redoc_url=None)
app.include_router(memeRouter, tags=["memeBingo"])

@app.exception_handler(OtherValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	return JSONResponse(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		content={'detail': jsonable_encoder(exc.errors())},
	)


PASSWORD_SALT = 'test'
MONGODB_URL = 'mongodb://root:example@localhost:27017'
mongoClient = MongoClient(MONGODB_URL, uuidRepresentation='standard')
mongoDb = mongoClient.get_database('test_meme')
cardsCollection = mongoDb.get_collection('cards')
cardsCollection.drop()
gamesCollection = mongoDb.get_collection('games')
gamesCollection.drop()

def cardsRepo():
	return CardsRepo(cardsCollection)

def gamesRepo():
	return GamesRepo(gamesCollection)

app.dependency_overrides[getCardsRepo] = cardsRepo
app.dependency_overrides[getGamesRepo] = gamesRepo

client = TestClient(app)


def test_createAndCloneCard():

	userId = 'qwe1234'

	# access denied
	response = client.post("/cards/")
	assert response.status_code == 403

	token = signToken({'userId':userId})
	client.cookies.set('at', token)

	# validation
	response = client.post("/cards/", params = {'userId':userId})
	assert response.status_code == 422

	# create
	card = {
			"phrases": [],
			"title": "string",
			"description": "string",
			}
	response = client.post("/cards/", params = {'userId':userId}, json=card )
	card2 = response.json()
	assert response.status_code == 201
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", card2['id']) is not None
	assert card['phrases'] == card2['phrases']
	assert card['title'] == card2['title']
	assert card['description'] == card2['description']
	

	# wrong get
	response = client.get('/cards/' + '123456')
	assert response.status_code == 404

	# get
	response = client.get('/cards/' + card2['id'])
	assert response.status_code == 200
	card3 = response.json()
	assert card2 == card3

	# clone
	response = client.post("/cards/" + card2['id'] + "/clone", params = {'userId':userId})
	card4 = response.json()
	assert response.status_code == 201
	assert card2 != card4
	assert card4['parentCardId'] == card2['id']

	# gets
	response = client.get('/cards/', params = {'ids':[card2['id'], card4['id']]})
	assert response.status_code == 200
	cards = response.json()
	assert len(cards) == 2
	assert card2 in cards
	assert card4 in cards


def test_updateAndDeleteCard():

	userId = 'qwe1'
	userId2 = 'qwe2'

	token = signToken({'userId':userId})
	client.cookies.set('at', token)

	# create
	card = {
			"phrases": [],
			"title": "string",
			"description": "string",
			}
	response = client.post("/cards/", params = {'userId':userId}, json=card )
	assert response.status_code == 201
	card2 = response.json()

	# update by owner
	card = {
			"phrases": ['hello'],
			"title": "title",
			"description": "",
			}
	response = client.put("/cards/" + card2['id'], params = {'userId':userId}, json=card)
	assert response.status_code == 200
	card3 = response.json()
	assert card3['title'] == 'title'
	assert card3['hidden'] == False

	# get
	response = client.get('/cards/' + card2['id'])
	assert response.status_code == 200
	card3 = response.json()
	assert card3['title'] == 'title'
	assert card3['hidden'] == False

	# hide
	response = client.delete("/cards/" + card2['id'], params = {'userId':userId})
	assert response.status_code == 200
	
	# get
	response = client.get('/cards/' + card2['id'])
	assert response.status_code == 200
	card3 = response.json()
	assert card3['title'] == 'title'
	assert card3['hidden'] == True


	token = signToken({'userId':userId2})
	client.cookies.set('at', token)

	# update by other
	card = {
			"phrases": ['hello2'],
			"title": "title2",
			"description": "",
			}
	response = client.put("/cards/" + card2['id'], params = {'userId':userId2}, json=card)
	assert response.status_code == 403
	
	# hide by other
	response = client.delete("/cards/" + card2['id'], params = {'userId':userId2})
	assert response.status_code == 403

	# get
	response = client.get('/cards/' + card2['id'])
	assert response.status_code == 200
	card3 = response.json()
	assert card3['title'] == 'title'
	assert card3['hidden'] == True


def test_getAndFindCard():

	userId = 'qwe3'
	userId2 = 'qwe4'

	# setup
	token = signToken({'userId':userId})
	client.cookies.set('at', token)

	data = {"phrases": [],"title": "string","description": "string", 'tags': ['ft1', 'ft2']}
	response = client.post("/cards/", params = {'userId':userId}, json=data )
	assert response.status_code == 201
	card11 = response.json()

	data = {"phrases": [],"title": "string","description": "string", 'tags': ['ft1',]}
	response = client.post("/cards/", params = {'userId':userId}, json=data )
	assert response.status_code == 201
	card12 = response.json()

	data = {"phrases": [],"title": "string","description": "string", 'tags': ['ft1', 'ft3']}
	response = client.post("/cards/", params = {'userId':userId}, json=data )
	assert response.status_code == 201
	card13 = response.json()

	token = signToken({'userId':userId2})
	client.cookies.set('at', token)

	data = {"phrases": [],"title": "string","description": "string", 'tags': ['ft1', 'ft2']}
	response = client.post("/cards/", params = {'userId':userId2}, json=data )
	assert response.status_code == 201
	card21 = response.json()

	data = {"phrases": [],"title": "string","description": "string", 'tags': ['ft1',]}
	response = client.post("/cards/", params = {'userId':userId2}, json=data )
	assert response.status_code == 201
	card22 = response.json()

	data = {"phrases": [],"title": "string","description": "string", 'tags': ['ft1', 'ft3']}
	response = client.post("/cards/", params = {'userId':userId2}, json=data )
	assert response.status_code == 201
	card23 = response.json()


	# find by tags and tags
	response = client.get('/cards', params={'tags': ['ft1']})
	assert response.status_code == 200
	list = response.json()
	assert len(list) == 6

	response = client.get('/cards', params={'tags': ['ft1', 'ft2']})
	assert response.status_code == 200
	list = response.json()
	assert len(list) == 2

	response = client.get('/cards', params={'tags': ['ft1', 'ft2', 'unknown']})
	assert response.status_code == 200
	list = response.json()
	assert len(list) == 0


	response = client.get('/cards/tags', params={'tags': ['ft2']})
	assert response.status_code == 200
	list = response.json()
	assert 'ft1' in list 
	assert 'ft2' in list

	response = client.get('/cards/tags', params={'tags': ['ft1', 'ft2', 'ft3']})
	assert response.status_code == 200
	list = response.json()
	assert list == []

	# wrong author
	response = client.get('/cards/myCards', params={'userId': userId})
	assert response.status_code == 403

	# right author
	response = client.get('/cards/myCards', params={'userId': userId2})
	assert response.status_code == 200
	list = response.json()
	assert list == [card23['id'], card22['id'], card21['id']]

	# is not owner
	response = client.get('/cards/{}/isOwner/{}'.format(card21['id'], userId))
	assert response.status_code == 200
	assert response.json() == False

	# is owner
	response = client.get('/cards/{}/isOwner/{}'.format(card21['id'], userId2))
	assert response.status_code == 200
	assert response.json() == True

	# not found card
	response = client.get('/cards/{}/isOwner/{}'.format('123123', userId))
	assert response.status_code == 404


def test_startUpdateAndHideCard():

	userId = 'qwe12345'
	userId2 = 'qwe123455'

	token = signToken({'userId':userId})
	client.cookies.set('at', token)

	# create card
	data = {"phrases": [], "title": "string", "description": "string"}
	response = client.post("/cards/", params = {'userId':userId}, json=data )
	card = response.json()
	cardId = card['id']

	# start game
	response = client.post("/games/", params = {'userId':userId, 'cardId': cardId} )
	assert response.status_code == 201
	game1 = response.json()
	assert game1['cardId'] == cardId
	gameId1 = game1['id']

	token = signToken({'userId':userId2})
	client.cookies.set('at', token)

	# start game userId2
	response = client.post("/games/", params = {'userId':userId2, 'cardId': cardId} )
	assert response.status_code == 201
	game2 = response.json()
	assert game2['cardId'] == cardId
	gameId2 = game2['id']

	# another one
	response = client.post("/games/", params = {'userId':userId2, 'cardId': cardId} )
	assert response.status_code == 201
	game3 = response.json()
	assert game3['cardId'] == cardId
	gameId3 = game3['id']


	# update
	response = client.put("/games/" + gameId2, params = {'userId':userId})
	assert response.status_code == 403

	response = client.put("/games/" + gameId2, params = {'userId':userId2}, json={'checkedPhrases': [1,2,3]})
	assert response.status_code == 200

	response = client.get("/games/" + gameId2)
	assert response.status_code == 200
	assert response.json()['checkedPhrases'] == [1,2,3]

	response = client.put("/games/" + gameId1, params = {'userId':userId2}, json={'checkedPhrases': [1,2,3]})
	assert response.status_code == 403


	# games of card
	response = client.get("/games/byCard/" + cardId, params={'userId': userId2})
	assert response.status_code == 200
	models = response.json()
	assert len(models) == 2
	gameIds = [model['id'] for model in models]
	assert gameId2 in gameIds	
	assert gameId3 in gameIds

	# hide
	response = client.delete("/games/" + gameId2, params = {'userId':userId})
	assert response.status_code == 403

	response = client.delete("/games/" + gameId2, params = {'userId':userId2})
	assert response.status_code == 200

	response = client.get("/games/" + gameId2)
	assert response.status_code == 200
	assert response.json()['hidden'] == True

	response = client.delete("/games/" + gameId1, params = {'userId':userId2})
	assert response.status_code == 403

	#not found
	response = client.get("/games/123123")
	assert response.status_code == 404

	# games of card
	response = client.get("/games/byCard/" + cardId, params={'userId': userId2})
	assert response.status_code == 200
	models = response.json()
	assert len(models) == 1
	gameIds = [model['id'] for model in models]
	assert gameId3 in gameIds


# unable for testing, cos user needed
# def test_canShare():

# 	userId = 'qwe1234567890'

# 	token = signToken({'userId':userId})
# 	client.cookies.set('at', token)

# 	# create card
# 	data = {"phrases": [], "title": "string", "description": "string"}
# 	response = client.post("/cards/", params = {'userId':userId}, json=data )
# 	card = response.json()
# 	cardId = card['id']

# 	# start game
# 	response = client.post("/games/", params = {'userId':userId, 'cardId': cardId} )
# 	assert response.status_code == 201
# 	game1 = response.json()
# 	assert game1['cardId'] == cardId
# 	gameId1 = game1['id']