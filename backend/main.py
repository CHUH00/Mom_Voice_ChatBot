import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.api import router

app = FastAPI(title="Mom Voice ChatBot API", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Mom Voice ChatBot Backend is Running"}
