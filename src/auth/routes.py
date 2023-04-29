from fastapi import APIRouter, Request, Response, Depends
from fastapi.exceptions import HTTPException
from .schemas import *
from .repo import *
from .jwt import *


async def getAuthRepo():
	return MemoAuthRepo()


async def getUsersRepo():
	return MemoUsersRepo()

router = APIRouter()


@router.get("/attributes")
async def getAttributes(userRepo: AbcUsersRepo = Depends(getUsersRepo), 
							payload:UserAttributes = Depends(getJWTPayload)) -> UserAttributes:
	userId = payload.get('userId', None)
	user = userRepo.get(userId)
	return UserAttributes() if user is None else UserAttributes.parse_obj(user) 


@router.put("/signup", status_code=201, dependencies=[Depends(accessControl(isNotAuthorized))])
async def signup(signupForm: SignupForm, response: Response,
				authRepo: AbcAuthRepo = Depends(getAuthRepo), 
				userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:

	try:
		# todo: транзакция
		user = userRepo.create(name=signupForm.name, isGuest=False)
		auth = authRepo.create(email=signupForm.email, password=signupForm.password, userId=user.id)
	except Exception as e:
		raise HTTPException(status_code=422, detail=[
							{'loc': ['body'], 'msg': str(e), 'type': 'create'}])

	# here can add additional data to payload from user attributes
	payload = {'userId':user.id}
	setTokens(response = response,  payload = payload)
	return UserAttributes.parse_obj(user)


@router.post("/login", dependencies=[Depends(accessControl(isNotAuthorized))])
async def login(loginForm: LoginForm, response: Response,
				authRepo: AbcAuthRepo = Depends(getAuthRepo), 
				userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:

	if not authRepo.checkPassword(loginForm.email, loginForm.password):
		# TODO: придумать вариант поприличней
		raise HTTPException(status_code=422, detail=[
							{'loc': ['body'], 'msg': 'wrong email or password', 'type': 'checkPassword'}])


	auth = authRepo.getByEmail(loginForm.email)
	user = userRepo.get(auth.userId)

	# here can add additional data to payload from user attributes
	payload = {'userId':user.id}
	setTokens(response = response,  payload = payload)
	return UserAttributes.parse_obj(user)


@router.post("/logout", dependencies=[Depends(accessControl(isAuthorized))])
async def logout(response: Response) -> UserAttributes:
	cleanTokens(response)
	return UserAttributes()


@router.put("/refresh")
async def refresh(request: Request, response: Response, 
					userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:
	payload = checkRefreshToken(request)
	user = userRepo.get(payload['userId'])
	# here can add additional data to payload from user attributes
	payload = {'userId':user.id}
	setTokens(response = response,  payload = payload)
	return UserAttributes.parse_obj(user)


@router.put("/signup-guest", status_code=201, dependencies=[Depends(accessControl(isNotAuthorized))])
async def signupGuest() -> UserAttributes:
	return UserAttributes(id='123')
