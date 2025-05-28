from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.routers import templates

app = FastAPI()

app.include_router(auth_router)
app.include_router(templates.router)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
