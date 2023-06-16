from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from memeBingo.routes import router as memeBingoRouter
from auth.routes import router as authRouter
from exceptions import OtherValidationError

import pathlib

def get_git_revision(base_path):
    git_dir = pathlib.Path(base_path) / '.git'
    with (git_dir / 'HEAD').open('r') as head:
        ref = head.readline().split(' ')[-1].strip()

    with (git_dir / ref).open('r') as git_hash:
        return git_hash.readline().strip()

app = FastAPI(redoc_url=None, version=get_git_revision('../')[0:7])

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

