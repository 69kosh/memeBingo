from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from memeBingo.routes import router as memeBingoRouter
from auth.routes import router as authRouter
from exceptions import OtherValidationError

app = FastAPI(redoc_url=None)

origins = [  # dev only!
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://meme1.local",
    "http://meme1.local:8080",
    "http://meme1.local:8081",
    "http://meme2.local",
    "http://meme2.local:8080",
    "http://meme2.local:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memeBingoRouter, tags=["memeBingo"])
app.include_router(authRouter, tags=["auth"], prefix='/auth')

@app.exception_handler(OtherValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'detail': jsonable_encoder(exc.errors())},
    )

