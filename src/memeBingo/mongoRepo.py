from .repo import *

from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()
PASSWORD_SALT = os.getenv('PASSWORD_SALT')
MONGODB_URL = os.getenv('MONGODB_URL')
mongoClient = MongoClient(MONGODB_URL, uuidRepresentation='standard')
mongoDb = mongoClient.get_database('meme')
cardsCollection = mongoDb.get_collection('cards')
gamesCollection = mongoDb.get_collection('games')


class CardsRepo(AbcCardsRepo):

	def findByTags(self, tags: list[str], limit: int = 100) -> list[str]:
		docs = cardsCollection.find(filter={'tags': {'$all': tags}} if len(tags) else None,
									projection={'_id': 1},
									sort=[("createdAt", -1)],
									limit=limit)
		return [doc['_id'] for doc in docs]

	def create(self, card: CardModel) -> CardModel | None:
		res = cardsCollection.insert_one(card.dict(by_alias=True))
		# print(res.inserted_id)
		return card if res.inserted_id else None

	def get(self, id: str) -> CardModel | None:
		data = cardsCollection.find_one({'_id': id})
		if data:
			return CardModel.parse_obj(data)

	def gets(self, ids: list[str]) -> list[CardModel]:
		docs = cardsCollection.find({'_id': {'$in': ids}})
		if docs:
			return [CardModel.parse_obj(doc) for doc in docs]

	def update(self, id: str, card: CardUpdateModel, conditions: dict = {}) -> bool:
		res = cardsCollection.update_one(
			filter=conditions | {'_id': id}, update={'$set': card.dict()})

		return res.modified_count == 1
	

	def hide(self, id: str, conditions: dict = {}) -> bool:
		res = cardsCollection.update_one(
			filter=conditions | {'_id': id}, update={'$set': {'hidden': True}})

		return res.modified_count == 1

	def findTagsByTags(self, tags: list[str], limit: int = 100) -> list[str]:
		result = cardsCollection.aggregate([
			{'$match': {'tags': {'$all': tags}} if len(tags) else {} },
			{'$sort': {'createdAt': -1}},
			{'$limit': limit },
			{'$project': { '_id': 0, 'tags': 1 } },
			{'$unwind': "$tags" },
			{'$group': {'_id': "$tags", 'sum': {'$sum': 1}}},
			{'$sort': {'sum': -1}}
		])
		return [doc['_id'] for doc in result]

	def findByAuthor(self, authorId: str, limit: int = 100) -> list[str]:
		docs = cardsCollection.find(filter={'authorId': authorId},
									projection={'_id': 1},
									sort=[("createdAt", -1)],
									limit=limit)
		return [doc['_id'] for doc in docs]


class GamesRepo(AbcGamesRepo):
	
	def get(self, id: str) -> GameModel:
		data = gamesCollection.find_one({'_id': id})
		if data:
			return GameModel.parse_obj(data)
	
	def getMyGamesByCard(self, cardId: str, ownerId: str) -> list[GameModel]:
		docs = gamesCollection.find(filter={'cardId': cardId, 'ownerId': ownerId},
									sort=[("createdAt", -1)])
		return [GameModel.parse_obj(doc) for doc in docs]

	def create(self, game: GameModel) -> GameModel:
		res = gamesCollection.insert_one(game.dict(by_alias=True))
		return game if res.inserted_id else None
	
	def update(self, id: str, game: GameUpdateModel, conditions: dict = {}) -> bool:
		res = gamesCollection.update_one(
			filter=conditions | {'_id': id}, update={'$set': game.dict()})

		return res.modified_count == 1
	
	def hide(self, id: str, conditions: dict = {}):
		res = gamesCollection.update_one(
			filter=conditions | {'_id': id}, update={'$set': {'hidden' : True}})

		return res.modified_count == 1

	def findCardsByOwner(self, ownerId: str, limit: int = 100) -> list[str]:
		result = gamesCollection.aggregate([
			{'$match': {'ownerId': ownerId}},
			{'$group': {'_id': "$cardId", 'lastGame': {'$max': '$createdAt'}}},
			{'$sort': {'lastGame': -1}},
			{'$limit': limit },
		])
		return [doc['_id'] for doc in result]
