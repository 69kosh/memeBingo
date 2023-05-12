import pytest
from auth.repo import *
from auth.memoRepo import AuthRepo as MemoAuthRepo, UsersRepo as MemoUsersRepo
from auth.mongoRepo import AuthRepo as MongoAuthRepo, UsersRepo as MongoUsersRepo
from pymongo import MongoClient


PASSWORD_SALT = 'test'
MONGODB_URL = 'mongodb://root:example@localhost:27017'
mongoClient = MongoClient(MONGODB_URL, uuidRepresentation='standard')
mongoDb = mongoClient.get_database('test_meme')
usersCollection = mongoDb.get_collection('users')
usersCollection.drop()
authCollection = mongoDb.get_collection('auth')
authCollection.drop()

@pytest.fixture(params=["memo", "mongo"])
def usersRepo(request):
	if request.param == 'memo':
		return MemoUsersRepo()
	elif request.param == 'mongo':
		return MongoUsersRepo(usersCollection)

@pytest.fixture(params=["memo", "mongo"])
def authRepo(request):
	if request.param == 'memo':
		return MemoAuthRepo()
	elif request.param == 'mongo':
		return MongoAuthRepo(authCollection, PASSWORD_SALT)

def test_createUser(usersRepo:AbcUsersRepo):
	assert usersRepo.get('not-existed') is None

	id = usersRepo.create('user123456', False)
	user = usersRepo.get(id)
	assert user is not None
	assert user.name == 'user123456'

	id = usersRepo.create('guest123456', True)
	user = usersRepo.get(id)
	assert user is not None
	assert user.name == 'guest123456'

def test_createAuth(authRepo:AbcAuthRepo):
	assert authRepo.getByEmail('not-existed@email.fake') is None

	email = authRepo.create('user1@email.fake', 'password1', 'userid1')
	auth = authRepo.getByEmail(email)
	assert auth is not None
	assert auth.userId == 'userid1'

	with pytest.raises(Exception):
		#same user
		email = authRepo.create('user1@email.fake', 'password1', 'userid1')

def test_checkAuth(authRepo:AbcAuthRepo):
	assert not authRepo.checkPassword('not-existed@email.fake', 'password1')

	authRepo.create('user2@email.fake', 'password1', 'userid1')
	assert not authRepo.checkPassword('not-existed@email.fake', 'password1')
	assert not authRepo.checkPassword('user2@email.fake', 'password2')
	assert authRepo.checkPassword('user2@email.fake', 'password1')