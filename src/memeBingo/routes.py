from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"Hello": "World"}


@router.get("/closed")
async def closed():
    return {"Hello": "Closed"}
