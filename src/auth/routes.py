from fastapi import APIRouter, Response, Depends
from fastapi.exceptions import HTTPException
from .schemas import *
from .repo import *
from .jwt import *


async def getAuthRepo():
    print('getAuthRepo')
    return MemoAuthRepo()


async def getUsersRepo():
    return MemoUsersRepo()

router = APIRouter()


@router.get("/attributes")
async def getUserAttributes() -> UserAttributes:
    return UserAttributes()


@router.put("/signup", status_code=201)
async def signup(signupForm: SignupForm) -> UserAttributes:
    return UserAttributes(id='123')


@router.post("/login")
async def login(loginForm: LoginForm, response: Response,
                authRepo: AbcAuthRepo = Depends(getAuthRepo), 
                userRepo: AbcUsersRepo = Depends(getUsersRepo)) -> UserAttributes:

    if not authRepo.checkPassword(loginForm.email, loginForm.password):
        # TODO: придумать другой варианты
        raise HTTPException(status_code=422, detail=[
                            {'loc': ['body'], 'msg': 'wrong email or password', 'type': 'checkPassword'}])


    auth = authRepo.getByEmail(loginForm.email)
    user = userRepo.get(auth.userId)
    attributes = UserAttributes.parse_obj(user)
    payload = {'userId': attributes.id}
    setTokens(response, payload)
    return attributes


@router.post("/logout")
async def logout():
    ...


@router.put("/refresh")
async def refresh() -> UserAttributes:
    return UserAttributes(id='123')


@router.put("/signup-guest", status_code=201)
async def signupGuest() -> UserAttributes:
    return UserAttributes(id='123')
