import pytest
from memeBingo.repo import *
# from memeBingo.memoRepo import AuthRepo as MemoAuthRepo, UsersRepo as MemoUsersRepo
from memeBingo.mongoRepo import CardsRepo as MongoCardsRepo, GamesRepo as MongoGamesRepo
from pymongo import MongoClient


PASSWORD_SALT = 'test'
MONGODB_URL = 'mongodb://root:example@localhost:27017'
mongoClient = MongoClient(MONGODB_URL, uuidRepresentation='standard')
mongoDb = mongoClient.get_database('test_meme')
cardsCollection = mongoDb.get_collection('cards')
cardsCollection.drop()
gamesCollection = mongoDb.get_collection('games')
gamesCollection.drop()


@pytest.fixture()
def cardsRepo():
	return MongoCardsRepo(cardsCollection)


@pytest.fixture()
def gamesRepo():
	return MongoGamesRepo(gamesCollection)


def test_createCard(cardsRepo: AbcCardsRepo):

	userId = 'qwe123'

	model = CardModel(authorId=userId, phrases=[], title='hello', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	assert cardsRepo.get(model.id) is None

	id = cardsRepo.create(model)

	assert id == model.id
	assert id == cardsRepo.get(model.id).id


def test_updateCard(cardsRepo: AbcCardsRepo):

	userId = 'qwe123'

	model = CardModel(authorId=userId, phrases=[], title='hello2', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	id = cardsRepo.create(model)

	updateModel = CardUpdateModel(phrases=['qwe'], title='hello2', description='hello2', tags=[],
								  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	assert cardsRepo.update(id, updateModel)
	assert cardsRepo.get(id).description == 'hello2'


def test_hideCard(cardsRepo: AbcCardsRepo):

	userId = 'qwe123'

	model = CardModel(authorId=userId, phrases=[], title='hello3', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	id = cardsRepo.create(model)

	assert cardsRepo.hide(id)
	assert cardsRepo.get(id).hidden


def test_getsCard(cardsRepo: AbcCardsRepo):

	userId = 'qwe123'
	model1 = CardModel(authorId=userId, phrases=[], title='hello11', description='', tags=[],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model2 = CardModel(authorId=userId, phrases=[], title='hello12', description='', tags=[],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model3 = CardModel(authorId=userId, phrases=[], title='hello13', description='', tags=[],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	id1 = cardsRepo.create(model1)
	id2 = cardsRepo.create(model2)
	id3 = cardsRepo.create(model3)

	ids = [id3, id2, id1]

	models = cardsRepo.gets(ids)
	print(models)

	for model in models:
		assert model.id in ids


def test_findByAuthorCard(cardsRepo: AbcCardsRepo):

	userId = 'qwe1235678'
	model1 = CardModel(authorId=userId, phrases=[], title='hello21', description='', tags=[],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model2 = CardModel(authorId=userId, phrases=[], title='hello22', description='', tags=[],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model3 = CardModel(authorId=userId, phrases=[], title='hello23', description='', tags=[],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	id1 = cardsRepo.create(model1)
	id2 = cardsRepo.create(model2)
	id3 = cardsRepo.create(model3)

	ids = [id3, id2, id1]

	ids2 = cardsRepo.findByAuthor(authorId=userId)
	
	assert len(ids2) == len(ids)

	for id in ids2:
		assert id in ids

def test_findByTagsCard(cardsRepo: AbcCardsRepo):

	userId = 'qwe123'
	model1 = CardModel(authorId=userId, phrases=[], title='hello21', description='', tags=['t1'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model2 = CardModel(authorId=userId, phrases=[], title='hello22', description='', tags=['t1', 't2'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model3 = CardModel(authorId=userId, phrases=[], title='hello23', description='', tags=['t1', 't2', 't3'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	id1 = cardsRepo.create(model1)
	id2 = cardsRepo.create(model2)
	id3 = cardsRepo.create(model3)

	ids = [id3, id2, id1]

	resIds = cardsRepo.findByTags(tags=['t3'])
	assert len(resIds) == 1
	assert id3 in resIds

	resIds = cardsRepo.findByTags(tags=['t2'])
	assert len(resIds) == 2
	assert id2 in resIds
	assert id3 in resIds

	resIds = cardsRepo.findByTags(tags=[])
	assert len(resIds) > 2
	assert id1 in resIds
	assert id2 in resIds
	assert id3 in resIds

def test_findTagsByTagsCard(cardsRepo: AbcCardsRepo):

	userId = 'qwe123'
	model1 = CardModel(authorId=userId, phrases=[], title='hello21', description='', tags=['t21'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model2 = CardModel(authorId=userId, phrases=[], title='hello22', description='', tags=['t21', 't22'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	model3 = CardModel(authorId=userId, phrases=[], title='hello23', description='', tags=['t21', 't22', 't23'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	id1 = cardsRepo.create(model1)
	id2 = cardsRepo.create(model2)
	id3 = cardsRepo.create(model3)

	ids = [id3, id2, id1]

	tags = cardsRepo.findTagsByTags(tags=['t23'])
	assert len(tags) == 3
	for tag in tags:
		assert tag in ['t21', 't22', 't23']



# def get(self, id: str) -> CardModel: ...

# def gets(self, ids: list[str]) -> list[CardModel]: ...

# def create(self, card: CardModel) -> CardModel: ...

# def update(self, id: str, card: CardUpdateModel, conditions: dict = {}) -> bool: ...

# def hide(self, id: str, conditions: dict = {}) -> bool: ...

# def findByTags(self, tags: list[str], limit:int = 100) -> list[str]: ...

# def findTagsByTags(self, tags: list[str], limit:int = 100) -> list[str]: ...

# def findByAuthor(self, authorId: str, limit: int = 100) -> list[str]: ...
