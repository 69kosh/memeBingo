from fastapi import APIRouter, Request, Response, Depends
from fastapi.exceptions import HTTPException
from .schemas import *
from .mongoRepo import *
from .jwt import *
from starlette.status import HTTP_404_NOT_FOUND
from exceptions import OtherValidationError
import random

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
import os

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

router = APIRouter()


@router.get("/attributes", dependencies=[Depends(checkAccess(mustBeAuthorized))])
async def getMyAttributes(userRepo: AbcUsersRepo = Depends(getUsersRepo),
						payload: dict = Depends(getJWTPayload)) -> UserAttributes:
	userId = payload.get('userId', None)
	user = userRepo.get(userId)
	return UserAttributes(id=userId) if user is None else UserAttributes.parse_obj(user)

@router.get("/attributes/{userId}")
async def getUserAttributes(userId: str, userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:
	user = userRepo.get(userId)
	if user is None:
		raise HTTPException(
			status_code=HTTP_404_NOT_FOUND,
			detail="Not found"
		)
	return UserAttributes.parse_obj(user)


@router.put("/signup", status_code=201, dependencies=[Depends(checkAccess(mustBeNotAuthorizedOrGuest))])
async def signup(signupForm: SignupForm, request: Request, response: Response,
				 authRepo: AbcAuthRepo = Depends(getAuthRepo),
				 userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:
	
	try:
		payload = checkRefreshToken(request)
		user = userRepo.get(payload['userId'])
	except:
		user = None

	if user is not None and user.isGuest == True:
		# merge user
		# todo: транзакция/откат	
		try:
			authId = authRepo.create(email=signupForm.email,
								password=signupForm.password, userId=user.id)
		except DuplicateKeyError as e:
			raise OtherValidationError(
				[{'loc': ['body', 'email'], 'msg': 'Email already exists', 'type': 'dublicate email'}])
		
		userId = userRepo.update(user.id, name=signupForm.name, isGuest=False)
	
	else:
		# new user
		# todo: транзакция/откат
		userId = userRepo.create(name=signupForm.name, isGuest=False)
		try:
			authId = authRepo.create(email=signupForm.email,
								password=signupForm.password, userId=userId)
		except DuplicateKeyError as e:
			raise OtherValidationError(
				[{'loc': ['body', 'email'], 'msg': 'Email already exists', 'type': 'dublicate email'}])

	# here can add additional data to payload from user attributes
	payload = {'userId': userId, 'isGuest': False}
	setTokens(response=response,  payload=payload)
	user = userRepo.get(userId)
	return UserAttributes() if user is None else UserAttributes.parse_obj(user)


@router.post("/login", dependencies=[Depends(checkAccess(mustBeNotAuthorizedOrGuest))])
async def login(loginForm: LoginForm, response: Response,
				authRepo: AbcAuthRepo = Depends(getAuthRepo),
				userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:

	if not authRepo.checkPassword(loginForm.email, loginForm.password):
		raise OtherValidationError(
			[{'loc': ['body'], 'msg': 'Wrong email or password', 'type': 'login'}])

	auth = authRepo.getByEmail(loginForm.email)
	user = userRepo.get(auth.userId)

	# here can add additional data to payload from user attributes
	payload = {'userId': user.id, 'isGuest': False}
	setTokens(response=response,  payload=payload)
	return UserAttributes.parse_obj(user)


# , dependencies=[Depends(accessControl(isAuthorized))])
@router.post("/logout")
async def logout(response: Response) -> UserAttributes:
	cleanTokens(response)
	return UserAttributes()


@router.get("/refresh")
async def refresh(request: Request, response: Response,
				  userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:
	payload = checkRefreshToken(request)
	user = userRepo.get(payload['userId'])
	if user is None:
		raise HTTPException(
			status_code=HTTP_403_FORBIDDEN,
			detail="Not authenticated"
		)
	# here can add additional data to payload from user attributes
	payload = {'userId': user.id, 'isGuest': False}
	setTokens(response=response,  payload=payload)
	return UserAttributes.parse_obj(user)


@router.put("/signup-guest", status_code=201, dependencies=[Depends(checkAccess(mustBeNotAuthorized))])
async def signupGuest(response: Response,
					  userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:
	id = userRepo.create(
		name='guest #' + str(random.randint(100000, 999999)), isGuest=True)
	# here can add additional data to payload from user attributes
	payload = {'userId': id, 'isGuest': True}
	setTokens(response=response,  payload=payload)
	user = userRepo.get(id)
	return UserAttributes() if user is None else UserAttributes.parse_obj(user)

