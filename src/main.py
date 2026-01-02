"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database.session import engine, Base
from src.api.routes import chat, sessions

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI Chatbot Service for analyzing Uber data",
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware
# Allow specific origins for production and local development
allowed_origins = [
    "https://main.d2hgspiyjkz5p5.amplifyapp.com",  # Production Amplify URL
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Chatbot Service API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

