from .repo import *

from pymongo.collection import Collection

class CardsRepo(AbcCardsRepo):
	
	def __init__(self, collection) -> None:
		super().__init__()
		self.collection:Collection = collection
	
	def create(self, card: CardModel) -> str | None:
		res = self.collection.insert_one(card.dict(by_alias=True))
		# print(res.inserted_id)
		return res.inserted_id if res.inserted_id else None

	def get(self, id: str) -> CardModel | None:
		data = self.collection.find_one({'_id': id})
		if data:
			return CardModel.parse_obj(data)

	def gets(self, ids: list[str]) -> list[CardModel]:
		docs = self.collection.find({'_id': {'$in': ids}})
		if docs:
			return [CardModel.parse_obj(doc) for doc in docs]

	def update(self, id: str, card: CardUpdateModel | CardSetIsGuestModel, conditions: dict = {}) -> bool:
		res = self.collection.update_one(
			filter=conditions | {'_id': id}, update={'$set': card.dict()})

		return res.modified_count == 1
	
	def hide(self, id: str, conditions: dict = {}) -> bool:
		res = self.collection.update_one(
			filter=conditions | {'_id': id}, update={'$set': {'hidden': True}})

		return res.modified_count == 1


	def findByTags(self, tags: list[str], limit: int = 100, 
                   withHidden:bool = False, withGuests:bool = False) -> list[str]:
		conds = {}
		if not withHidden:
			conds['hidden'] = False
		if not withGuests:
			conds['isGuest'] = False

		docs = self.collection.find(filter=({'tags': {'$all': tags}} | conds) if len(tags) else conds,
									projection={'_id': 1},
									sort=[("createdAt", -1)],
									limit=limit)
		return [doc['_id'] for doc in docs]

	def findTagsByTags(self, tags: list[str], limit: int = 100, 
                   withHidden:bool = False, withGuests:bool = False) -> list[str]:
		conds = {}
		if len(tags):
			conds['tags'] = {'$all': tags}
		if not withHidden:
			conds['hidden'] = False
		if not withGuests:
			conds['isGuest'] = False

		result = self.collection.aggregate([
			{'$match': conds},
			{'$sort': {'createdAt': -1}},
			{'$limit': limit },
			{'$project': { '_id': 0, 'tags': 1 } },
			{'$unwind': "$tags" },
			{'$group': {'_id': "$tags", 'sum': {'$sum': 1}}},
			{'$sort': {'sum': -1}}
		])
		return [doc['_id'] for doc in result]

	def findByAuthor(self, authorId: str, limit: int = 100, withHidden: bool = False) -> list[str]:
		docs = self.collection.find(filter={'authorId': authorId} | ({} if withHidden else {'hidden': False}),
									projection={'_id': 1},
									sort=[("createdAt", -1)],
									limit=limit)
		return [doc['_id'] for doc in docs]
	
	def filterCardsByHidden(self, cardIds, limit: int = 100) -> list[str]:
		docs = self.collection.find(filter={'_id':{'$in':cardIds}, 'hidden': False},
							projection={'_id': 1})
		ids = [doc['_id'] for doc in docs]
		return [id for id in cardIds if id in ids]


class GamesRepo(AbcGamesRepo):
	def __init__(self, collection) -> None:
		super().__init__()
		self.collection:Collection = collection

	def get(self, id: str) -> GameModel:
		data = self.collection.find_one({'_id': id})
		if data:
			return GameModel.parse_obj(data)
	
	def getMyGamesByCard(self, cardId: str, ownerId: str) -> list[GameModel]:
		docs = self.collection.find(filter={'cardId': cardId, 'ownerId': ownerId, 'hidden': False},
									sort=[("createdAt", -1)])
		return [GameModel.parse_obj(doc) for doc in docs]

	def create(self, game: GameModel) -> str:
		res = self.collection.insert_one(game.dict(by_alias=True))
		return res.inserted_id if res.inserted_id else None
	
	def update(self, id: str, game: GameUpdateModel | GameSetIsGuestModel, conditions: dict = {}) -> bool:
		res = self.collection.update_one(
			filter=conditions | {'_id': id}, update={'$set': game.dict()})

		return res.modified_count == 1
	
	def hide(self, id: str, conditions: dict = {}):
		res = self.collection.update_one(
			filter=conditions | {'_id': id}, update={'$set': {'hidden' : True}})

		return res.modified_count == 1

	def findCardsByOwner(self, ownerId: str, limit: int = 100, withHidden: bool = False) -> list[str]:
		result = self.collection.aggregate([
			{'$match': {'ownerId': ownerId} | ({} if withHidden else {'hidden': False})},
			{'$group': {'_id': "$cardId", 'lastGame': {'$max': '$createdAt'}}},
			{'$sort': {'lastGame': -1}},
			{'$limit': limit }
		])
		return [doc['_id'] for doc in result]
	

	def findByOwner(self, ownerId: str, limit: int = 100, withHidden: bool = False) -> list[str]:
		docs = self.collection.find(filter={'ownerId': ownerId} | ({} if withHidden else {'hidden': False}),
									projection={'_id': 1},
									sort=[("createdAt", -1)],
									limit=limit)
		return [doc['_id'] for doc in docs]

	def getCountByCard(self, cardId: str) -> int:
		return self.collection.count_documents(filter={'cardId': cardId})