from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv

# Import routers
from routes import speech_to_text, text_to_speech, chat

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Voice Agent API",
    description="Production-level FastAPI server for Voice Agent system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(speech_to_text.router, prefix="/api", tags=["speech-to-text"])
app.include_router(text_to_speech.router, prefix="/api", tags=["text-to-speech"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    """Health check endpoint compatible with GET and HEAD"""
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"message": "Voice Agent API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "speech_to_text": "available",
            "text_to_speech": "available", 
            "chat": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 