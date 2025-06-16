# Support Bot API

A voice-based technical support agent API for LATAM companies, built with FastAPI.

## 🚀 Features

- Multi-tenant architecture
- Voice call handling via Twilio
- Semantic search in company manuals
- AI-powered responses using GPT-4

## 🛠️ Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```env
# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Support Bot API

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# OpenAI
OPENAI_API_KEY=your-openai-api-key
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

## 🚀 Running with Docker

### Build and start the stack (API + Postgres)

```bash
docker-compose up --build
```

- The API will be available at [http://localhost:8000](http://localhost:8000)
- The Postgres database will be available at `localhost:5432`

### Stopping the stack

```bash
docker-compose down
```

### Running Alembic migrations

```bash
docker-compose exec web alembic upgrade head
```

## 🐳 Docker-related files
- `Dockerfile`: Builds the FastAPI app image
- `docker-compose.yml`: Orchestrates the app and Postgres
- `.dockerignore`: Excludes files from Docker build context

## 📚 API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🏗️ Project Structure

```
support_bot/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   └── chroma/
│   ├── models/
│   │   └── tenant.py
│   ├── schemas/
│   │   └── tenant.py
│   └── main.py
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## 🔒 Security

- All endpoints are protected with Twilio signature verification
- Environment variables for sensitive data
- Rate limiting implemented
- Input sanitization
- CORS policies configured

## 📝 License

MIT 