# Medical AI Backend

A FastAPI-based medical diagnosis API that analyzes symptoms and provides disease predictions.

## Features

- Symptom analysis using AI language models
- FAISS-based vector matching for fast symptom comparison
- CORS support for cross-origin requests
- Emergency detection and health suggestions

## API Endpoints

### Health Check
```
GET /health
```

### Diagnose Symptoms
```
POST /diagnose
```
Request body:
```json
{
  "symptoms": "fever, cough, headache"
}
```

## Setup

1. Install dependencies:
```
pip install fastapi uvicorn python-dotenv sentence-transformers faiss-cpu numpy
```

2. Set up environment variables in a `.env` file:
```
API_KEY=your_together_ai_api_key
```

3. Run the server:
```
uvicorn app:app --reload
```

## Model Information

The system uses:
- Together AI with Meta Llama 3 70B model for symptom refinement and fallback diagnosis
- FAISS and Sentence Transformers for vector similarity matching of symptoms

## Security Notes

- The API has CORS enabled for all origins (`*`). For production, limit this to specific origins.
- API keys should be properly secured via environment variables. 