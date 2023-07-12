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
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1', isGuest=False)
	model2 = CardModel(authorId=userId, phrases=[], title='hello22', description='', tags=['t1', 't2'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1', isGuest=False)
	model3 = CardModel(authorId=userId, phrases=[], title='hello23', description='', tags=['t1', 't2', 't3'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1', isGuest=False)
	
	model4 = CardModel(authorId=userId, phrases=[], title='hello23', description='', tags=['t1', 't2', 't3'],
					   outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1', isGuest=True)

	id1 = cardsRepo.create(model1)
	id2 = cardsRepo.create(model2)
	id3 = cardsRepo.create(model3)
	id4 = cardsRepo.create(model4)

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


	resIds = cardsRepo.findByTags(tags=['t3'], withGuests=True)
	assert len(resIds) == 2
	assert id3 in resIds
	assert id4 in resIds

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



def test_createAndUpdateAndHideGame(cardsRepo: AbcCardsRepo, gamesRepo: AbcGamesRepo):

	userId = 'qwe123'

	card = CardModel(authorId=userId, phrases=[], title='hello', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	id = cardsRepo.create(card)

	game = GameModel(cardId=id, ownerId=userId)

	gameId = gamesRepo.create(game)

	assert gameId == game.id
	assert gameId == gamesRepo.get(gameId).id
	assert not gamesRepo.get(gameId).hidden
	assert gamesRepo.update(gameId, GameUpdateModel(checkedPhrases=[1,2,3]))
	assert gamesRepo.get(gameId).checkedPhrases == [1,2,3]
	assert not gamesRepo.get(gameId).hidden
	assert gamesRepo.hide(gameId)
	assert gamesRepo.get(gameId).hidden

def test_getMyGamesByCard(cardsRepo: AbcCardsRepo, gamesRepo: AbcGamesRepo):

	userId = 'qwe123'

	card = CardModel(authorId=userId, phrases=[], title='hello', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')

	cardId = cardsRepo.create(card)

	game1 = GameModel(cardId=cardId, ownerId=userId)
	game2 = GameModel(cardId=cardId, ownerId=userId)
	game3 = GameModel(cardId=cardId, ownerId=userId)

	gameId1 = gamesRepo.create(game1)
	gameId2 = gamesRepo.create(game2)
	gameId3 = gamesRepo.create(game3)
	ids = [gameId1, gameId2, gameId3]
	
	games = gamesRepo.getMyGamesByCard(cardId, userId)
	for game in games:
		assert game.id in ids

def test_findCardsByOwner(cardsRepo: AbcCardsRepo, gamesRepo: AbcGamesRepo):

	userId = 'qwe'

	card1 = CardModel(authorId=userId, phrases=[], title='hello', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	cardId1 = cardsRepo.create(card1)
	game1 = GameModel(cardId=cardId1, ownerId=userId)
	gameId1 = gamesRepo.create(game1)

	card2 = CardModel(authorId=userId, phrases=[], title='hello', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	cardId2 = cardsRepo.create(card2)
	game2 = GameModel(cardId=cardId2, ownerId=userId)
	gameId2 = gamesRepo.create(game2)

	card3 = CardModel(authorId=userId, phrases=[], title='hello', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	cardId3 = cardsRepo.create(card3)
	game3 = GameModel(cardId=cardId3, ownerId=userId)
	gameId3 = gamesRepo.create(game3)

	card4 = CardModel(authorId=userId, phrases=[], title='hello', description='', tags=[],
					  outlineColor='c1', textColor='c2', backgroundColor='c3', markType='1')
	cardId4 = cardsRepo.create(card4) # will not found

	ids = [cardId1, cardId2, cardId3]
	
	cardIds = gamesRepo.findCardsByOwner(userId)

	for id in cardIds:
		assert id in ids
