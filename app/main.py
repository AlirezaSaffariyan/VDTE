from fastapi import FastAPI
from app.auth.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
