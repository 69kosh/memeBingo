from fastapi import APIRouter, Response
from .schemas import *

router = APIRouter()


@router.get("/features")
async def features() -> UserFeatures:
    return UserFeatures()

@router.put("/singup", status_code=201)
async def singup(singupForm: SingupForm) -> UserFeatures:
    return UserFeatures(id='123')

@router.post("/login")
async def login(loginForm:LoginForm) -> UserFeatures:
    return UserFeatures(id='123')

@router.post("/logout")
async def logout():
    ...

@router.put("/merge")
async def merge() -> UserFeatures:
    return UserFeatures(id='123')
