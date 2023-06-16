from fastapi.testclient import TestClient
from auth.routes import router as authRouter, getAuthRepo, getUsersRepo
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from auth.repo import *
from auth.memoRepo import AuthRepo as MemoAuthRepo, UsersRepo as MemoUsersRepo
from auth.mongoRepo import AuthRepo as MongoAuthRepo, UsersRepo as MongoUsersRepo
from pymongo import MongoClient
from exceptions import OtherValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

import re

app = FastAPI(redoc_url=None)
app.include_router(authRouter, tags=["auth"], prefix='/auth')

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
usersCollection = mongoDb.get_collection('users')
usersCollection.drop()
authCollection = mongoDb.get_collection('auth')
authCollection.drop()

# @pytest.fixture(params=["memo", "mongo"])


def usersRepo(type):
	def inner():
		if type == 'memo':
			return MemoUsersRepo()
		elif type == 'mongo':
			return MongoUsersRepo(usersCollection)
	return inner

# @pytest.fixture(params=["memo", "mongo"])


def authRepo(type):
	def inner():
		if type == 'memo':
			return MemoAuthRepo()
		elif type == 'mongo':
			return MongoAuthRepo(authCollection, PASSWORD_SALT)
	return inner


app.dependency_overrides[getAuthRepo] = authRepo('mongo')
app.dependency_overrides[getUsersRepo] = usersRepo('mongo')

client = TestClient(app)


def test_signup_guest():

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}
	# signup
	response = client.put("/auth/signup-guest")
	assert response.status_code == 201
	attr = response.json()
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", attr['id']) is not None
	assert attr['isGuest']
	assert re.match("guest #[0-9]{6}", attr['name']) is not None

	# denied repeated signup
	response = client.put("/auth/signup-guest")
	assert response.status_code == 403

	# check attributes
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	attr2 = response.json()
	assert attr == attr2

	# logout
	response = client.post("/auth/logout")
	assert response.status_code == 200

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}

	# check attributes
	response = client.get("/auth/attributes/{userId}".format(userId = attr['id']))
	assert response.status_code == 200
	attr2 = response.json()
	assert attr == attr2

	# check attributes
	response = client.get("/auth/attributes/123456")
	assert response.status_code == 404


def test_signup():

	email = 'fake@mail.fake'
	emailInvalid = 'mail.fake'
	name = 'test_user1'
	nameInvalid = 'in'
	password = 'password1'
	passwordInvalid = 'invalid'
	email2 = 'fake22@mail.fake'
	name2 = 'test_user122'
	password2 = 'password122'


	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}

	# signup try
	response = client.put("/auth/signup")
	assert response.status_code == 422

	# signup try2
	response = client.put(
		"/auth/signup", json={'email': emailInvalid, 'name': nameInvalid, 'password': passwordInvalid})
	assert response.status_code == 422
	assert response.json() == {'detail': [{'loc': ['body', 'name'], 'msg': 'ensure this value has at least 3 characters',
										   'type': 'value_error.any_str.min_length', 'ctx': {'limit_value': 3}},
										  {'loc': ['body', 'email'], 'msg': 'value is not a valid email address',
										   'type': 'value_error.email'},
										  {'loc': ['body', 'password'], 'msg': 'ensure this value has at least 8 characters',
										   'type': 'value_error.any_str.min_length', 'ctx': {'limit_value': 8}}]}

	# signup
	response = client.put(
		"/auth/signup", json={'email': email, 'name': name, 'password': password})
	assert response.status_code == 201
	attr = response.json()
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", attr['id']) is not None
	assert not attr['isGuest']
	assert attr['name'] == name

	# denied repeated signup
	response = client.put("/auth/signup")
	assert response.status_code == 403

	# check attributes
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	attr2 = response.json()
	assert attr == attr2

	# logout
	response = client.post("/auth/logout")
	assert response.status_code == 200

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}

	# signup dublicate email
	response = client.put(
		"/auth/signup", json={'email': email, 'name': name, 'password': password})
	assert response.status_code == 422
	assert response.json() == {'detail': [{'loc': ['body', 'email'], 
					'msg': 'Email already exists', 'type': 'dublicate email'}]}


	# signup Guest
	response = client.put("/auth/signup-guest")
	assert response.status_code == 201
	attr = response.json()
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", attr['id']) is not None
	assert attr['isGuest']
	assert re.match("guest #[0-9]{6}", attr['name']) is not None

	# signup dublicate email
	response = client.put(
		"/auth/signup", json={'email': email, 'name': name, 'password': password})
	assert response.status_code == 422
	assert response.json() == {'detail': [{'loc': ['body', 'email'], 
					'msg': 'Email already exists', 'type': 'dublicate email'}]}

	# signup over guest
	response = client.put(
		"/auth/signup", json={'email': email2, 'name': name2, 'password': password2})
	assert response.status_code == 201
	attr2 = response.json()
	assert attr2['id'] == attr['id']
	assert attr2['isGuest'] == False
	assert attr2['name'] == name2

	# logout
	response = client.post("/auth/logout")
	assert response.status_code == 200

def test_login():

	email = 'fake2@mail.fake'
	emailInvalid = 'mail.fake'
	name = 'test_user2'
	password = 'password2'
	passwordInvalid = 'invalid'
	passwordWrong = '2password'

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}
	
	# signup
	response = client.put(
		"/auth/signup", json={'email': email, 'name': name, 'password': password})
	assert response.status_code == 201
	attr = response.json()
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", attr['id']) is not None
	assert not attr['isGuest']
	assert attr['name'] == name
	
	# logout
	response = client.post("/auth/logout")
	assert response.status_code == 200

	# login try
	response = client.post(
		"/auth/login", json={'email': emailInvalid, 'password': passwordInvalid})
	assert response.status_code == 422
	print(response.json())
	assert response.json() == {'detail': [{'loc': ['body', 'email'], 'msg': 'value is not a valid email address', 
										   'type': 'value_error.email'}, 
										   {'loc': ['body', 'password'], 'msg': 'ensure this value has at least 8 characters', 
											'type': 'value_error.any_str.min_length', 'ctx': {'limit_value': 8}}]}
	
	# login try 2
	response = client.post(
		"/auth/login", json={'email': email, 'password': passwordWrong})
	assert response.status_code == 422
	print(response.json())
	assert response.json() == {'detail': [{'loc': ['body'], 'msg': 'Wrong email or password', 'type': 'login'}]}
	
	# login
	response = client.post(
		"/auth/login", json={'email': email, 'password': password})
	assert response.status_code == 200
	attr = response.json()
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", attr['id']) is not None
	assert not attr['isGuest']
	assert attr['name'] == name

	# denied repeated login
	response = client.post(
		"/auth/login", json={'email': email, 'password': password})
	assert response.status_code == 403

	# check attributes
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	attr2 = response.json()
	assert attr == attr2

	# logout
	response = client.post("/auth/logout")
	assert response.status_code == 200

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}

	# signup guest
	response = client.put("/auth/signup-guest")
	assert response.status_code == 201

	# login
	response = client.post(
		"/auth/login", json={'email': email, 'password': password})
	assert response.status_code == 200
	attr = response.json()
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", attr['id']) is not None
	assert not attr['isGuest']
	assert attr['name'] == name

	# logout
	response = client.post("/auth/logout")
	assert response.status_code == 200

def test_refresh():

	email = 'fake3@mail.fake'
	emailInvalid = 'mail.fake'
	name = 'test_user3'
	password = 'password3'
	passwordInvalid = 'invalid'
	passwordWrong = '3password'

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}
	
	# signup
	response = client.put(
		"/auth/signup", json={'email': email, 'name': name, 'password': password})
	assert response.status_code == 201
	attr = response.json()
	assert re.match(
		"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", attr['id']) is not None
	assert not attr['isGuest']
	assert attr['name'] == name
	
	# del access token
	client.cookies.delete('at')

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}

	# refresh
	response = client.get("/auth/refresh")
	assert response.status_code == 200
	
	# check attributes
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	attr2 = response.json()
	assert attr == attr2

	# logout
	response = client.post("/auth/logout")
	assert response.status_code == 200

	# try refresh
	response = client.get("/auth/refresh")
	assert response.status_code == 403

	# not registered
	response = client.get("/auth/attributes")
	assert response.status_code == 200
	assert response.json() == {
		"id": None,
		"isGuest": None,
		"name": None,
	}