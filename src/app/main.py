from fastapi import FastAPI
from app.features.endpoints.chat import router as chat_router

app = FastAPI()

app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Server running"}
