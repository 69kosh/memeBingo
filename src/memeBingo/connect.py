from pymongo import MongoClient

from dotenv import load_dotenv
import os

from .mongoRepo import *


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
