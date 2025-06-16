from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.core.middleware import RequestIDMiddleware, TenantMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Request ID middleware
app.add_middleware(RequestIDMiddleware)

# Add Tenant middleware
app.add_middleware(TenantMiddleware)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Support Bot API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

# Import and include API router
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_STR) 