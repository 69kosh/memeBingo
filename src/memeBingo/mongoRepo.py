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
        print(res.inserted_id)
        return card if res.inserted_id else None

    def get(self, id:str) -> CardModel | None:
        data = cardsCollection.find_one({'_id':id})
        if data:
            return CardModel.parse_obj(data)

    # def create(self, name: str, isGuest = False) -> UserModel:
    #     user = UserModel(name=name, isGuest=isGuest)
    #     usersCollection.insert_one(user.dict(by_alias=True))
    #     return user
