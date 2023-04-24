from fastapi import FastAPI
from memeBingo.routes import router as memeBingoRouter
from auth.routes import router as authRouter

app = FastAPI()

app.include_router(memeBingoRouter, tags=["memeBingo"])
app.include_router(authRouter, tags=["auth"], prefix='/auth')