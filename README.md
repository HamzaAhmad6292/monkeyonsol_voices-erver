# Voice Agent FastAPI Server

A production-level FastAPI server for the Voice Agent system, migrated from Next.js API routes. This server provides speech-to-text, text-to-speech, and chat functionality using ElevenLabs and Groq APIs.

## Features

- **Speech-to-Text**: Convert audio to text using ElevenLabs API
- **Text-to-Speech**: Convert text to speech using ElevenLabs API
- **Chat**: LLM interactions using Groq API
- **Production Ready**: Docker support, logging, error handling
- **OpenAPI Documentation**: Auto-generated API docs
- **CORS Support**: Cross-origin resource sharing enabled

## Project Structure

```
voice_server/
├── main.py                 # FastAPI application entry point
├── schemas.py             # Pydantic models for request/response validation
├── requirements.txt       # Python dependencies
├── Dockerfile            # Production Docker configuration
├── env.example           # Environment variables template
├── README.md             # This file
├── routes/               # API route handlers
│   ├── __init__.py
│   ├── speech_to_text.py
│   ├── text_to_speech.py
│   └── chat.py
└── services/             # Business logic and API integrations
    ├── __init__.py
    ├── elevenlabs_service.py
    └── groq_service.py
```

## Setup

### Prerequisites

- Python 3.11+
- ElevenLabs API key
- Groq API key

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd voice_server
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Run the server:**
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t voice-agent-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 --env-file .env voice-agent-api
   ```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check

### Speech-to-Text
- `POST /api/speech-to-text` - Convert audio to text

**Multipart Form Data:**
```bash
curl -X POST "http://localhost:8000/api/speech-to-text" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.webm" \
  -F "model_id=scribe_v1"
```

**JSON with Base64:**
```bash
curl -X POST "http://localhost:8000/api/speech-to-text" \
  -H "Content-Type: application/json" \
  -d '{
    "audio": "base64_encoded_audio_data",
    "format": "webm",
    "model_id": "scribe_v1"
  }'
```

### Text-to-Speech
- `POST /api/text-to-speech` - Convert text to speech

```bash
curl -X POST "http://localhost:8000/api/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test message.",
    "voice_name": "Bill",
    "model_id": "eleven_monolingual_v2",
    "voice_settings": {
      "stability": 0.3,
      "similarity_boost": 0.7,
      "style": 0.8,
      "use_speaker_boost": true
    }
  }' \
  --output speech.mp3
```

### Chat
- `POST /api/chat` - LLM chat completion

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ],
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes |
| `GROQ_API_KEY` | Groq API key | Yes |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8000) | No |
| `DEBUG` | Debug mode (default: false) | No |

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Production Deployment

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  voice-agent-api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Using Gunicorn (Production)

For production deployment with Gunicorn:

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Configuration

For production, ensure:

1. **CORS Configuration**: Update `CORS_ORIGINS` in `.env` with actual frontend URLs
2. **API Keys**: Use secure environment variable management
3. **Logging**: Configure appropriate log levels
4. **SSL/TLS**: Use reverse proxy (nginx) for HTTPS

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input data
- **500 Internal Server Error**: Server-side errors
- **502 Bad Gateway**: External API errors (ElevenLabs/Groq)

All errors return structured JSON responses with error details.

## Logging

The application uses structured logging with different levels:

- **INFO**: Normal operations
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging (when enabled)

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Configure appropriate origins for production
3. **Rate Limiting**: Consider implementing rate limiting
4. **Input Validation**: All inputs are validated using Pydantic
5. **HTTPS**: Use HTTPS in production

## Migration Notes

This FastAPI server is a direct migration from the Next.js API routes:

- **Original**: `/api/speech-to-text` → **New**: `/api/speech-to-text`
- **Original**: `/api/text-to-speech` → **New**: `/api/text-to-speech`
- **Original**: `/api/chat` → **New**: `/api/chat`

The API maintains the same request/response structure for seamless integration with existing frontend applications. 