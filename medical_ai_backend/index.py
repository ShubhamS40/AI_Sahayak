import faiss
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Define Request Model
class SymptomsRequest(BaseModel):
    symptoms: str

# ✅ Load Hugging Face Embedding Model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ✅ Updated dataset with food recommendations & medicine dosage
medical_data = [
    {"symptoms": "fever, cough, sore throat", "disease": "Flu", 
     "medicines": [{"name": "Paracetamol", "dosage": "1 tablet morning & night"}, 
                   {"name": "Cough Syrup", "dosage": "2 teaspoons night"}],
     "precautions": ["Drink warm fluids", "Rest"], 
     "food": ["Ginger tea", "Chicken soup", "Citrus fruits", "Honey"]},

    {"symptoms": "headache, nausea", "disease": "Migraine", 
     "medicines": [{"name": "Ibuprofen", "dosage": "1 tablet morning"}, 
                   {"name": "Sumatriptan", "dosage": "1 tablet during attack"}],
     "precautions": ["Avoid bright lights", "Stay hydrated"], 
     "food": ["Nuts", "Leafy greens", "Magnesium-rich foods", "Whole grains"]},

    {"symptoms": "chest pain, shortness of breath", "disease": "Heart Attack", 
     "medicines": [{"name": "Aspirin", "dosage": "1 tablet daily"}, 
                   {"name": "Nitroglycerin", "dosage": "As prescribed by doctor"}],
     "precautions": ["Call emergency", "Stay calm"], 
     "food": ["Oats", "Salmon", "Berries", "Olive oil"]},

    {"symptoms": "high fever, rash, joint pain", "disease": "Dengue", 
     "medicines": [{"name": "Acetaminophen", "dosage": "1 tablet every 6 hours"}],
     "precautions": ["Drink plenty of fluids", "Avoid aspirin"], 
     "food": ["Papaya leaf juice", "Coconut water", "Pomegranate", "Kiwi"]},

    {"symptoms": "fatigue, dry skin, increased thirst", "disease": "Diabetes", 
     "medicines": [{"name": "Metformin", "dosage": "1 tablet morning & night"}, 
                   {"name": "Insulin", "dosage": "As per doctor prescription"}],
     "precautions": ["Monitor blood sugar", "Exercise daily"], 
     "food": ["Leafy greens", "Brown rice", "Nuts", "Beans"]},

    {"symptoms": "chills, sweating, high fever", "disease": "Malaria", 
     "medicines": [{"name": "Chloroquine", "dosage": "1 tablet morning & night"}, 
                   {"name": "Artemisinin", "dosage": "As per prescription"}],
     "precautions": ["Use mosquito nets", "Take anti-malarial drugs"], 
     "food": ["Porridge", "Fruits", "Coconut water", "Herbal tea"]},

    {"symptoms": "vomiting, nausea, abdominal pain", "disease": "Food Poisoning", 
     "medicines": [{"name": "ORS", "dosage": "After every loose motion"}, 
                   {"name": "Anti-emetics", "dosage": "As per prescription"}],
     "precautions": ["Stay hydrated", "Eat bland food"], 
     "food": ["Bananas", "Rice", "Applesauce", "Toast"]},

    {"symptoms": "persistent cough, weight loss, night sweats", "disease": "Tuberculosis", 
     "medicines": [{"name": "Isoniazid", "dosage": "1 tablet morning"}, 
                   {"name": "Rifampin", "dosage": "1 tablet night"}],
     "precautions": ["Cover mouth while coughing", "Take full medication course"], 
     "food": ["Eggs", "Milk", "Almonds", "Lean meat"]},

    {"symptoms": "difficulty swallowing, throat pain", "disease": "Tonsillitis", 
     "medicines": [{"name": "Antibiotics", "dosage": "As per prescription"}, 
                   {"name": "Painkillers", "dosage": "As needed"}],
     "precautions": ["Gargle with salt water", "Avoid cold drinks"], 
     "food": ["Warm tea", "Honey", "Mashed potatoes", "Yogurt"]}
]

# ✅ Convert symptoms to Hugging Face embeddings
symptom_texts = [entry["symptoms"] for entry in medical_data]
symptom_embeddings = embedding_model.encode(symptom_texts, convert_to_numpy=True)

# ✅ Store embeddings in FAISS for fast search
dimension = symptom_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)  # L2 Distance (Euclidean)
index.add(symptom_embeddings)

# ✅ Search Function
def find_disease(user_symptoms):
    user_embedding = embedding_model.encode([user_symptoms], convert_to_numpy=True)
    _, closest_match = index.search(user_embedding, 1)
    best_match_idx = closest_match[0][0]

    # Return matched disease details
    if best_match_idx >= 0:
        matched_disease = medical_data[best_match_idx]
        return {
            "disease": matched_disease["disease"],
            "medicines": [{"name": med["name"], "dosage": med["dosage"]} for med in matched_disease["medicines"]],
            "precautions": matched_disease["precautions"],
            "food": matched_disease["food"]
        }
    else:
        return {"error": "No matching disease found"}

# ✅ FastAPI Endpoint
@app.post("/diagnose")
def diagnose(request: SymptomsRequest):
    result = find_disease(request.symptoms)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# ✅ Run with: `uvicorn filename:app --reload`
