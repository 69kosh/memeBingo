from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from dotenv import load_dotenv
import os

from .mongoRepo import *


load_dotenv()
PASSWORD_SALT = os.getenv('PASSWORD_SALT')
MONGODB_URL = os.getenv('MONGODB_URL')
mongoClient = MongoClient(MONGODB_URL, uuidRepresentation='standard')
mongoDb = mongoClient.get_database('meme')
usersCollection = mongoDb.get_collection('users')
authCollection = mongoDb.get_collection('auth')


async def getAuthRepo():
	return AuthRepo(authCollection, PASSWORD_SALT)

async def getUsersRepo():
	return UsersRepo(usersCollection)

