from fastapi import APIRouter, Request, Response, Depends
from fastapi.exceptions import HTTPException
from .schemas import *
from .mongoRepo import *
from .jwt import *
from exceptions import OtherValidationError
import random

async def getAuthRepo():
	return AuthRepo()


async def getUsersRepo():
	return UsersRepo()

router = APIRouter()


@router.get("/attributes")
async def getAttributes(userRepo: AbcUsersRepo = Depends(getUsersRepo), 
							payload:dict = Depends(getJWTPayload)) -> UserAttributes:
	userId = payload.get('userId', None)
	user = userRepo.get(userId)
	return UserAttributes() if user is None else UserAttributes.parse_obj(user) 


@router.put("/signup", status_code=201, dependencies=[Depends(checkAccess(mustBeNotAuthorized))])
async def signup(signupForm: SignupForm, response: Response,
				authRepo: AbcAuthRepo = Depends(getAuthRepo), 
				userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:

	try:
		# todo: транзакция/откат
		user = userRepo.create(name=signupForm.name, isGuest=False)
		auth = authRepo.create(email=signupForm.email, password=signupForm.password, userId=user.id)
	except DuplicateKeyError as e:
		raise OtherValidationError([{'loc': ['body', 'email'], 'msg': 'Email already exists', 'type': 'dublicate email'}])
	
	# except ValueError as e:
	# 	raise OtherValidationError([{'loc': ['body'], 'msg': str(e), 'type': 'model validation error'}])

	# here can add additional data to payload from user attributes
	payload = {'userId':user.id}
	setTokens(response = response,  payload = payload)
	return UserAttributes.parse_obj(user)


@router.post("/login", dependencies=[Depends(checkAccess(mustBeNotAuthorized))])
async def login(loginForm: LoginForm, response: Response,
				authRepo: AbcAuthRepo = Depends(getAuthRepo), 
				userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:

	if not authRepo.checkPassword(loginForm.email, loginForm.password):
		raise OtherValidationError([{'loc': ['body'], 'msg': 'Wrong email or password', 'type': 'login'}])

	auth = authRepo.getByEmail(loginForm.email)
	user = userRepo.get(auth.userId)

	# here can add additional data to payload from user attributes
	payload = {'userId':user.id}
	setTokens(response = response,  payload = payload)
	return UserAttributes.parse_obj(user)


@router.post("/logout") # , dependencies=[Depends(accessControl(isAuthorized))])
async def logout(response: Response) -> UserAttributes:
	cleanTokens(response)
	return UserAttributes()


@router.put("/refresh")
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
	payload = {'userId':user.id}
	setTokens(response = response,  payload = payload)
	return UserAttributes.parse_obj(user)


@router.put("/signup-guest", status_code=201, dependencies=[Depends(checkAccess(mustBeNotAuthorized))])
async def signupGuest(response: Response, 
				userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:
	user = userRepo.create(name='guest #' + str(random.randint(100000, 999999)), isGuest=True)
	# here can add additional data to payload from user attributes
	payload = {'userId':user.id}
	setTokens(response = response,  payload = payload)
	return UserAttributes.parse_obj(user)