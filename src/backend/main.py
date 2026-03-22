from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root():
    return {"message": "Welcome to Resume NLP Analyzer API"}

from src.backend.api.routers import user, hr

app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(hr.router, prefix="/api/hr", tags=["hr"])
