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

	# update
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
