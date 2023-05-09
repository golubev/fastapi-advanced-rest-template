from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.api_router import api_router

application = FastAPI()
application.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
application.include_router(api_router)
