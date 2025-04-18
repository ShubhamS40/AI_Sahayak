import faiss
import numpy as np
import json
import requests
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Define request model
class SymptomsRequest(BaseModel):
    symptoms: str

# Load embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Set up Gemini API
GEMINI_API_KEY = "AIzaSyDhXtxSH8c2cGZnhpTskIIGHhbSa0_MKdk"  # Replace with your API key
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText?key={GEMINI_API_KEY}"

# Medical Data
medical_data = [
    {"symptoms": "fever, cough, sore throat", "disease": "Flu", "diagnosis": "Influenza", 
     "medicines": ["Paracetamol"], "tests": ["Rapid Influenza Test"], "precautions": ["Rest", "Hydration"], 
     "food": ["Soup", "Warm fluids"], "emergency": False},
    
    {"symptoms": "severe headache, nausea", "disease": "Brain Tumor", "diagnosis": "Abnormal brain growth", 
     "medicines": ["Dexamethasone"], "tests": ["MRI Brain"], "precautions": ["Surgery", "Radiation Therapy"], 
     "food": ["Protein-rich diet"], "emergency": True},

    {"symptoms": "chest pain, shortness of breath", "disease": "Heart Attack", "diagnosis": "Myocardial Infarction", 
     "medicines": ["Aspirin", "Nitroglycerin"], "tests": ["ECG", "Troponin Test"], "precautions": ["No exertion", "Oxygen"], 
     "food": ["Low-fat diet", "Omega-3"], "emergency": True},

    {"symptoms": "frequent urination, excessive thirst, fatigue", "disease": "Diabetes", "diagnosis": "High blood sugar levels", 
     "medicines": ["Metformin"], "tests": ["Fasting Blood Sugar", "HbA1c"], "precautions": ["Exercise", "Diet control"], 
     "food": ["Low-carb diet", "Leafy greens"], "emergency": False},

    {"symptoms": "high fever, chills, vomiting", "disease": "Malaria", "diagnosis": "Parasitic infection from mosquitoes", 
     "medicines": ["Chloroquine"], "tests": ["Blood Smear Test"], "precautions": ["Mosquito nets", "Anti-malarial drugs"], 
     "food": ["Fruits", "Plenty of fluids"], "emergency": True},

    {"symptoms": "bloody diarrhea, stomach cramps", "disease": "Food Poisoning", "diagnosis": "Bacterial or viral gastroenteritis", 
     "medicines": ["ORS", "Anti-diarrheal"], "tests": ["Stool Culture"], "precautions": ["Hydration", "Rest"], 
     "food": ["Boiled rice", "Yogurt"], "emergency": False},

    {"symptoms": "difficulty breathing, chest tightness", "disease": "Asthma", "diagnosis": "Inflammation of airways", 
     "medicines": ["Salbutamol Inhaler"], "tests": ["Spirometry"], "precautions": ["Avoid allergens", "Use inhaler"], 
     "food": ["Omega-3 foods", "Vitamin C"], "emergency": True},

    {"symptoms": "intense headache, sensitivity to light", "disease": "Migraine", "diagnosis": "Neurological disorder", 
     "medicines": ["Sumatriptan"], "tests": ["Neurological Exam"], "precautions": ["Avoid stress", "Hydration"], 
     "food": ["Magnesium-rich foods"], "emergency": False},

    {"symptoms": "joint pain, morning stiffness", "disease": "Arthritis", "diagnosis": "Inflammation of joints", 
     "medicines": ["Ibuprofen"], "tests": ["X-ray", "Rheumatoid Factor Test"], "precautions": ["Exercise", "Physiotherapy"], 
     "food": ["Omega-3", "Turmeric"], "emergency": False},

    {"symptoms": "persistent cough, weight loss, night sweats", "disease": "Tuberculosis", "diagnosis": "Bacterial lung infection", 
     "medicines": ["Rifampin", "Isoniazid"], "tests": ["Mantoux Test", "Chest X-ray"], "precautions": ["Isolation", "Medication adherence"], 
     "food": ["High-protein diet"], "emergency": True},

    {"symptoms": "frequent urination, pelvic pain", "disease": "Urinary Tract Infection (UTI)", "diagnosis": "Bacterial bladder infection", 
     "medicines": ["Ciprofloxacin"], "tests": ["Urine Culture"], "precautions": ["Hydration", "Avoid caffeine"], 
     "food": ["Cranberry juice", "Probiotics"], "emergency": False},

    {"symptoms": "dizziness, fatigue, pale skin", "disease": "Anemia", "diagnosis": "Low red blood cell count", 
     "medicines": ["Iron Supplements"], "tests": ["CBC Test"], "precautions": ["Iron-rich diet"], 
     "food": ["Spinach", "Red meat"], "emergency": False},

    {"symptoms": "nausea, yellow skin, fatigue", "disease": "Hepatitis", "diagnosis": "Liver infection (viral)", 
     "medicines": ["Antiviral Drugs"], "tests": ["Liver Function Test"], "precautions": ["Avoid alcohol", "Rest"], 
     "food": ["Leafy greens", "Garlic"], "emergency": True},

    {"symptoms": "abdominal pain, blood in stool", "disease": "Colon Cancer", "diagnosis": "Malignant tumor in colon", 
     "medicines": ["Chemotherapy"], "tests": ["Colonoscopy"], "precautions": ["High-fiber diet", "Avoid red meat"], 
     "food": ["Whole grains", "Legumes"], "emergency": True},

    {"symptoms": "blurred vision, eye pain", "disease": "Glaucoma", "diagnosis": "Optic nerve damage due to pressure", 
     "medicines": ["Timolol Eye Drops"], "tests": ["Eye Pressure Test"], "precautions": ["Regular eye check-ups"], 
     "food": ["Leafy greens", "Omega-3"], "emergency": True},

    {"symptoms": "difficulty speaking, facial drooping", "disease": "Stroke", "diagnosis": "Brain blood flow blockage", 
     "medicines": ["Aspirin", "Clot-busting drugs"], "tests": ["CT Scan", "MRI"], "precautions": ["Low-sodium diet", "Exercise"], 
     "food": ["Fruits", "Nuts"], "emergency": True},

    {"symptoms": "tingling hands, fatigue, hair loss", "disease": "Thyroid Disorder", "diagnosis": "Hormonal imbalance in thyroid gland", 
     "medicines": ["Levothyroxine"], "tests": ["TSH Test"], "precautions": ["Avoid excessive soy", "Regular thyroid checkups"], 
     "food": ["Iodine-rich foods", "Seafood"], "emergency": False},

    {"symptoms": "uncontrolled shaking, slow movement", "disease": "Parkinson’s Disease", "diagnosis": "Nervous system disorder", 
     "medicines": ["Levodopa"], "tests": ["Neurological Exam"], "precautions": ["Physical therapy", "Balanced diet"], 
     "food": ["High-protein diet", "Bananas"], "emergency": True}
]


# **Step 1: Embed each individual symptom, not full text**
all_symptoms = [symptom for entry in medical_data for symptom in entry["symptoms"]]
all_embeddings = embedding_model.encode(all_symptoms, convert_to_numpy=True)

# Create FAISS index
dimension = all_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(all_embeddings)

THRESHOLD = 3.0  # Lowered for better accuracy

# **Function to refine symptoms using Gemini AI**
def refine_with_gemini(prompt: str, system_prompt: str):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"role": "system", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }
    try:
        response = requests.post(GEMINI_URL, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("candidates", [{}])[0].get("output", "") or None
    except requests.exceptions.RequestException as e:
        print(f"Gemini API Error: {e}")
        return None

# **Function to clean and parse JSON response**
def clean_json_response(response):
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        return None

# **AI-generated suggestion for the user**
def generate_ai_suggestion(disease: str, food: list, emergency: bool):
    seriousness = "⚠️ Critical! Seek medical attention immediately." if emergency else "🟢 Not critical, but consult a doctor."
    food_recommendation = f"🍏 Recommended foods: {', '.join(food)}" if food else "🍏 Maintain a healthy diet."
    return f"You might have *{disease}*. {seriousness} {food_recommendation}"

# **Improved disease matching using individual symptom comparison**
def find_best_disease(symptom_list):
    total_scores = {}

    for symptom in symptom_list:
        symptom_embedding = embedding_model.encode([symptom])
        distances, indices = index.search(symptom_embedding, 1)

        if distances[0][0] < THRESHOLD:
            matched_symptom = all_symptoms[indices[0][0]]
            for entry in medical_data:
                if matched_symptom in entry["symptoms"]:
                    if entry["disease"] in total_scores:
                        total_scores[entry["disease"]] += 1
                    else:
                        total_scores[entry["disease"]] = 1

    if not total_scores:
        return None

    best_match = max(total_scores, key=total_scores.get)
    for entry in medical_data:
        if entry["disease"] == best_match:
            return entry

    return None

# **Main API route**
@app.post("/diagnose")
def diagnose(request: SymptomsRequest):
    # **Step 1: Refine Hinglish user input**
    refined_symptoms = refine_with_gemini(
        request.symptoms, "Refine these medical symptoms for better diagnosis:"
    ) or request.symptoms

    # **Step 2: Split symptoms and find the best disease**
    symptom_list = refined_symptoms.lower().split(", ")
    best_match = find_best_disease(symptom_list)

    if not best_match:
        # **Fallback to AI diagnosis if no exact match found**
        system_prompt = """You are a medical expert. Provide a structured JSON response:
        {
            "disease": "Name",
            "diagnosis": "Description...",
            "medicines": ["..."],
            "tests": ["..."],
            "precautions": ["..."],
            "food": ["..."],
            "emergency": boolean,
            "alert": "Critical condition warning" (if applicable)
        }"""
        ai_response = refine_with_gemini(f"Symptoms: {refined_symptoms}", system_prompt)
        response = clean_json_response(ai_response) if ai_response else None
        if not response:
            return {"error": "❌ No matching disease found. Please consult a doctor."}
    else:
        response = best_match.copy()
        if best_match["emergency"]:
            response["alert"] = "⚠️ This is a critical condition! Seek medical help."

    # **Step 4: Generate AI-based health suggestion**
    response["ai_suggestion"] = generate_ai_suggestion(
        response["disease"], response.get("food", []), response.get("emergency", False)
    )

    return response