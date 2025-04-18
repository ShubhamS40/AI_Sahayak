"""
FastAPI CORS Fix for the AI Sahayak backend

Instructions:
1. Install required dependency: pip install fastapi-cors
2. Add the following lines to your existing FastAPI app (app.py):

# Add these imports at the top
from fastapi.middleware.cors import CORSMiddleware

# Add this after your app = FastAPI() line:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production use specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

3. Restart your FastAPI server
"""

# Here's a complete example with CORS enabled
import faiss
import numpy as np
import json
import requests
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rest of your code remains the same 
# ...

# To test that your CORS is working, use this route
@app.get("/test-cors")
def test_cors():
    return {"message": "CORS is working!"}

# Make sure your /health route returns proper JSON
@app.get("/health")
def health_check():
    return {"status": "online", "name": "AI Sahayak Backend"}
