import faiss
import numpy as np
import json
import requests
import re
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

app = FastAPI(title="Medical AI API", description="API for medical diagnosis based on symptoms")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - adjust this in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request model
class SymptomsRequest(BaseModel):
    symptoms: str

# Define response model
class DiagnosisResponse(BaseModel):
    disease: str
    diagnosis: str
    medicines: List[str]
    tests: List[str]
    precautions: List[str]
    food: List[str]
    emergency: bool
    ai_suggestion: str
    alert: Optional[str] = None
    confidence_score: Optional[float] = None
    matched_symptoms: Optional[List[str]] = None
    action_plan: Optional[str] = None

# Load embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Set up Together AI API
TOGETHER_AI_API_KEY = os.getenv("API_KEY", "dbd65ef3ea28743eb9f6ed0df90a98971c5a014ec4ddbd3fca2bf087de1a73e0")
TOGETHER_AI_URL = "https://api.together.xyz/v1/completions"  # Fixed API endpoint

# Common disease entries to add at the beginning of the list
common_diseases = [
    {"symptoms": "cold, runny nose, sneezing", "disease": "Common Cold", "diagnosis": "Viral infection causing upper respiratory symptoms", 
     "medicines": ["Decongestants", "Antihistamines", "Paracetamol"], "tests": ["No specific tests required"], 
     "precautions": ["Rest", "Hydration", "Hand hygiene"], 
     "food": ["Warm soups", "Herbal teas", "Honey with ginger"], "emergency": False},
    
    {"symptoms": "cough, cold, sore throat, runny nose, stuffy nose", "disease": "Common Cold", "diagnosis": "Viral infection of the upper respiratory tract", 
     "medicines": ["Paracetamol", "Antihistamines", "Decongestants"], "tests": ["No specific tests needed"], 
     "precautions": ["Rest", "Hydration", "Avoid cold exposure"], 
     "food": ["Warm soups", "Herbal teas", "Honey with ginger"], "emergency": False},
    
    {"symptoms": "headache, mild pain, tension", "disease": "Tension Headache", "diagnosis": "Common headache caused by muscle tension or stress", 
     "medicines": ["Ibuprofen", "Paracetamol"], "tests": ["None required for occasional headaches"], 
     "precautions": ["Rest", "Stress management", "Good posture"], 
     "food": ["Stay hydrated", "Regular meals", "Reduce caffeine"], "emergency": False},
     
    {"symptoms": "fever, mild fever, temperature", "disease": "Viral Fever", "diagnosis": "Temporary increase in body temperature due to viral infection", 
     "medicines": ["Paracetamol", "Ibuprofen"], "tests": ["Complete blood count if persistent"], 
     "precautions": ["Rest", "Hydration", "Light clothing"], 
     "food": ["Light, easily digestible foods", "Broths", "Fruit juices"], "emergency": False},
     
    {"symptoms": "stomach pain, abdominal discomfort, bloating, gas", "disease": "Indigestion", "diagnosis": "Discomfort in upper abdomen, often after eating", 
     "medicines": ["Antacids", "H2 blockers"], "tests": ["None for occasional symptoms"], 
     "precautions": ["Eat slowly", "Avoid trigger foods", "Small frequent meals"], 
     "food": ["Bland foods", "Ginger tea", "Avoid spicy foods"], "emergency": False},
     
    {"symptoms": "fever, cough, sore throat, runny nose", "disease": "Flu", "diagnosis": "Influenza virus infection", 
     "medicines": ["Paracetamol", "Oseltamivir"], "tests": ["Rapid Influenza Test", "PCR test"], 
     "precautions": ["Rest", "Hydration", "Isolation"], 
     "food": ["Chicken soup", "Warm fluids", "Citrus fruits"], "emergency": False},
     
    {"symptoms": "diarrhea, stomach pain, nausea, vomiting", "disease": "Gastroenteritis", "diagnosis": "Inflammation of the stomach and intestines, often from infection", 
     "medicines": ["ORS", "Probiotics", "Loperamide"], "tests": ["Stool test if severe or persistent"], 
     "precautions": ["Hydration", "Rest", "Hand hygiene"], 
     "food": ["BRAT diet (bananas, rice, applesauce, toast)", "Clear fluids", "Avoid dairy"], "emergency": False},
]

# Combine medical data, starting with common diseases
medical_data = common_diseases + [
    {"symptoms": "fever, headache, body aches, chills, fatigue", "disease": "Typhoid", "diagnosis": "Bacterial infection caused by Salmonella typhi",
     "medicines": ["Ciprofloxacin", "Azithromycin"], "tests": ["Blood culture", "Widal test"], 
     "precautions": ["Avoid raw foods", "Drink clean water", "Isolation"], 
     "food": ["Soft, easily digestible foods", "Boiled vegetables", "Yogurt"], "emergency": True},
     
    # Keep the remaining entries from the original medical_data list
    {"symptoms": "severe headache, nausea, vomiting, light sensitivity", "disease": "Migraine", "diagnosis": "Neurological disorder with recurrent headaches", 
     "medicines": ["Sumatriptan", "Ibuprofen"], "tests": ["Neurological exam", "MRI in persistent cases"], 
     "precautions": ["Avoid triggers", "Rest in dark room", "Cold compress"], 
     "food": ["Avoid processed foods", "Magnesium-rich foods", "Stay hydrated"], "emergency": False},
     
    {"symptoms": "headache, fever, stiff neck, confusion", "disease": "Meningitis", "diagnosis": "Inflammation of the membranes surrounding the brain and spinal cord", 
     "medicines": ["Antibiotics", "Corticosteroids"], "tests": ["Lumbar puncture", "Blood culture"], 
     "precautions": ["Immediate medical attention", "Isolation if bacterial"], 
     "food": ["Balanced diet", "Plenty of fluids"], "emergency": True},
    
    {"symptoms": "severe headache, nausea", "disease": "Brain Tumor", "diagnosis": "Abnormal brain growth", 
     "medicines": ["Dexamethasone"], "tests": ["MRI Brain", "CT Scan"], "precautions": ["Surgery", "Radiation Therapy"], 
     "food": ["Protein-rich diet", "Anti-inflammatory foods"], "emergency": True},

    {"symptoms": "chest pain, shortness of breath, sweating", "disease": "Heart Attack", "diagnosis": "Myocardial Infarction", 
     "medicines": ["Aspirin", "Nitroglycerin", "Beta blockers"], "tests": ["ECG", "Troponin Test", "Coronary angiography"], 
     "precautions": ["Emergency medical attention", "Rest", "Oxygen"], 
     "food": ["Low-fat diet", "Omega-3 rich foods", "Mediterranean diet"], "emergency": True},

    {"symptoms": "frequent urination, excessive thirst, fatigue, blurred vision", "disease": "Diabetes", "diagnosis": "High blood sugar levels due to insulin issues", 
     "medicines": ["Metformin", "Insulin"], "tests": ["Fasting Blood Sugar", "HbA1c", "Glucose tolerance test"], 
     "precautions": ["Regular monitoring", "Exercise", "Diet control"], 
     "food": ["Low-carb diet", "High-fiber foods", "Leafy greens", "Avoid sugary foods"], "emergency": False},

    {"symptoms": "high fever, chills, headache, muscle pain, fatigue", "disease": "Malaria", "diagnosis": "Parasitic infection from mosquitoes", 
     "medicines": ["Chloroquine", "Artemisinin-based therapy"], "tests": ["Blood Smear Test", "Rapid diagnostic test"], 
     "precautions": ["Mosquito nets", "Insect repellent", "Anti-malarial drugs for prevention"], 
     "food": ["Fruits", "Vegetables", "Plenty of fluids"], "emergency": True},

    {"symptoms": "jaundice, yellow eyes, dark urine, fatigue, abdominal pain", "disease": "Jaundice", "diagnosis": "Yellowing of skin due to high bilirubin levels", 
     "medicines": ["Depends on cause"], "tests": ["Liver function tests", "Bilirubin levels", "Ultrasound"], 
     "precautions": ["Rest", "Hydration", "Avoid alcohol"], 
     "food": ["Low-fat diet", "Fresh fruits and vegetables", "Avoid red meat"], "emergency": True},
      
    {"symptoms": "bloody diarrhea, stomach cramps, nausea, vomiting", "disease": "Food Poisoning", "diagnosis": "Bacterial or viral gastroenteritis", 
     "medicines": ["ORS", "Anti-diarrheal", "Probiotics"], "tests": ["Stool Culture", "Blood tests"], 
     "precautions": ["Hydration", "Rest", "Mild foods"], 
     "food": ["Boiled rice", "Bananas", "Toast", "Yogurt"], "emergency": False},

    {"symptoms": "difficulty breathing, wheezing, chest tightness, coughing", "disease": "Asthma", "diagnosis": "Chronic inflammation of airways", 
     "medicines": ["Salbutamol Inhaler", "Corticosteroids"], "tests": ["Spirometry", "Peak flow meter"], 
     "precautions": ["Avoid triggers", "Use inhalers properly", "Action plan"], 
     "food": ["Omega-3 rich foods", "Vitamin C and E sources", "Ginger"], "emergency": True},

    {"symptoms": "joint pain, swelling, stiffness, reduced mobility", "disease": "Arthritis", "diagnosis": "Inflammation of joints", 
     "medicines": ["Ibuprofen", "Disease-modifying antirheumatic drugs"], "tests": ["X-ray", "Rheumatoid Factor Test", "Anti-CCP"], 
     "precautions": ["Regular exercise", "Joint protection", "Physiotherapy"], 
     "food": ["Omega-3 rich foods", "Turmeric", "Ginger", "Antioxidant-rich fruits"], "emergency": False},

    {"symptoms": "persistent cough, weight loss, night sweats, blood in sputum", "disease": "Tuberculosis", "diagnosis": "Bacterial lung infection caused by Mycobacterium tuberculosis", 
     "medicines": ["Rifampin", "Isoniazid", "Ethambutol", "Pyrazinamide"], "tests": ["Mantoux Test", "Chest X-ray", "Sputum culture"], 
     "precautions": ["Isolation during infectious period", "Complete medication course", "Ventilation"], 
     "food": ["High-protein diet", "Vitamin-rich foods", "Adequate calories"], "emergency": True},

    {"symptoms": "burning urination, frequent urination, pelvic pain, cloudy urine", "disease": "Urinary Tract Infection (UTI)", "diagnosis": "Bacterial infection in urinary system", 
     "medicines": ["Ciprofloxacin", "Nitrofurantoin"], "tests": ["Urine Culture", "Urinalysis"], 
     "precautions": ["Hydration", "Complete antibiotics course", "Proper hygiene"], 
     "food": ["Cranberry juice", "Probiotics", "Water", "Vitamin C foods"], "emergency": False},

    {"symptoms": "dizziness, fatigue, pale skin, shortness of breath, cold hands and feet", "disease": "Anemia", "diagnosis": "Low red blood cell or hemoglobin levels", 
     "medicines": ["Iron Supplements", "Vitamin B12", "Folic acid"], "tests": ["CBC Test", "Ferritin levels", "Vitamin B12 levels"], 
     "precautions": ["Iron-rich diet", "Treating underlying cause"], 
     "food": ["Spinach", "Red meat", "Beans", "Vitamin C sources"], "emergency": False},

    {"symptoms": "nausea, yellow skin, fatigue, abdominal pain, dark urine", "disease": "Hepatitis", "diagnosis": "Liver inflammation (viral or toxin-induced)", 
     "medicines": ["Antiviral Drugs", "Interferon"], "tests": ["Liver Function Test", "Hepatitis serology", "Liver biopsy"], 
     "precautions": ["Avoid alcohol", "Rest", "Vaccination for prevention"], 
     "food": ["Leafy greens", "Garlic", "Low-fat foods", "Avoid processed foods"], "emergency": True},

    {"symptoms": "abdominal pain, blood in stool, weight loss, changes in bowel habits", "disease": "Colon Cancer", "diagnosis": "Malignant tumor in colon", 
     "medicines": ["Chemotherapy", "Targeted therapy"], "tests": ["Colonoscopy", "Biopsy", "CT scan"], 
     "precautions": ["Regular screening", "Surgery if indicated"], 
     "food": ["Whole grains", "Legumes", "Fruits and vegetables", "Limit red meat"], "emergency": True},

    {"symptoms": "blurred vision, eye pain, halos around lights, gradual vision loss", "disease": "Glaucoma", "diagnosis": "Optic nerve damage due to increased eye pressure", 
     "medicines": ["Timolol Eye Drops", "Latanoprost"], "tests": ["Eye Pressure Test", "Visual field test", "Optical coherence tomography"], 
     "precautions": ["Regular eye check-ups", "Proper medication use"], 
     "food": ["Leafy greens", "Omega-3 rich foods", "Colorful fruits and vegetables"], "emergency": True},

    {"symptoms": "difficulty speaking, facial drooping, arm weakness, sudden confusion", "disease": "Stroke", "diagnosis": "Brain blood flow blockage or hemorrhage", 
     "medicines": ["Aspirin", "Clot-busting drugs", "Blood thinners"], "tests": ["CT Scan", "MRI", "Carotid ultrasound"], 
     "precautions": ["Immediate emergency care", "Blood pressure control"], 
     "food": ["Low-sodium diet", "Mediterranean diet", "Fruits", "Nuts"], "emergency": True},

    {"symptoms": "tingling hands, fatigue, hair loss, weight changes, sensitivity to cold", "disease": "Thyroid Disorder", "diagnosis": "Hormonal imbalance in thyroid gland", 
     "medicines": ["Levothyroxine", "Anti-thyroid medications"], "tests": ["TSH Test", "T3/T4 levels", "Thyroid antibodies"], 
     "precautions": ["Regular medication", "Periodic testing"], 
     "food": ["Iodine-rich foods", "Selenium-rich foods", "Avoid excessive soy"], "emergency": False},

    {"symptoms": "uncontrolled shaking, slow movement, stiffness, balance problems", "disease": "Parkinson's Disease", "diagnosis": "Progressive nervous system disorder", 
     "medicines": ["Levodopa", "Dopamine agonists"], "tests": ["Neurological Exam", "DaTscan"], 
     "precautions": ["Physical therapy", "Occupational therapy", "Exercise"], 
     "food": ["Antioxidant-rich foods", "High-fiber diet", "Omega-3 fatty acids"], "emergency": True},
      
    {"symptoms": "red rash, itching, skin inflammation", "disease": "Dermatitis", "diagnosis": "Skin inflammation condition", 
     "medicines": ["Corticosteroid creams", "Antihistamines"], "tests": ["Physical examination", "Patch testing"], 
     "precautions": ["Avoid triggers", "Gentle skin care", "Moisturize regularly"], 
     "food": ["Anti-inflammatory foods", "Omega-3 rich foods", "Avoid food triggers"], "emergency": False},
      
    {"symptoms": "sore throat, difficulty swallowing, swollen tonsils, fever", "disease": "Tonsillitis", "diagnosis": "Inflammation of the tonsils", 
     "medicines": ["Antibiotics", "Pain relievers"], "tests": ["Throat culture", "Rapid strep test"], 
     "precautions": ["Rest", "Gargling with salt water", "Complete antibiotic course"], 
     "food": ["Soft foods", "Cold liquids", "Warm teas", "Popsicles"], "emergency": False}
]

# Initialize FAISS index
def init_faiss_index():
    # Extract individual symptoms, not full text
    all_symptoms = []
    for entry in medical_data:
        symptoms = entry["symptoms"].split(", ")
        all_symptoms.extend(symptoms)
    
    # Create embeddings and index
    all_embeddings = embedding_model.encode(all_symptoms, convert_to_numpy=True)
    dimension = all_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(all_embeddings)
    
    return index, all_symptoms

# Initialize FAISS index once at startup
index, all_symptoms = init_faiss_index()
THRESHOLD = 3.0  # Lowered for better accuracy

# Function to process symptoms using Together AI
def process_with_together_ai(prompt: str, system_prompt: str) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {TOGETHER_AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use a more compatible format for the API
    data = {
        "model": "mixtral-8x7b-instruct-v0.1",  # Simplified model name
        "prompt": f"{system_prompt}\n\n{prompt}",
        "max_tokens": 800,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(TOGETHER_AI_URL, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["text"].strip()
        return None
    except requests.exceptions.RequestException as e:
        print(f"Together AI API Error: {e}")
        print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
        return None
    except Exception as e:
        print(f"Unexpected error with AI processing: {e}")
        return None

# Function to clean and parse JSON response
def clean_json_response(response: str) -> Optional[Dict[str, Any]]:
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"JSON parsing error: {e}")
        return None

# AI-generated suggestion for the user
def generate_ai_suggestion(disease: str, food: list, emergency: bool) -> str:
    seriousness = "⚠️ Critical! Seek medical attention immediately." if emergency else "🟢 Not critical, but consult a doctor."
    food_recommendation = f"🍏 Recommended foods: {', '.join(food)}" if food else "🍏 Maintain a healthy diet."
    return f"You might have *{disease}*. {seriousness} {food_recommendation}"

# Improved disease matching with better text processing
def find_best_disease(symptom_list: List[str]) -> Optional[Dict[str, Any]]:
    if not symptom_list:
        return None
    
    # Handle common phrases and extract symptoms
    processed_symptoms = []
    for symptom in symptom_list:
        # Clean up common phrases like "I have a cold" -> "cold"
        cleaned = re.sub(r'^i have (a|an)?', '', symptom).strip()
        cleaned = re.sub(r'^having (a|an)?', '', cleaned).strip()
        cleaned = re.sub(r'^suffering from (a|an)?', '', cleaned).strip()
        
        # Add the cleaned symptom
        if cleaned:
            processed_symptoms.append(cleaned)
    
    # If no valid symptoms after processing, return None
    if not processed_symptoms:
        return None
    
    # Use the processed symptoms for matching
    symptom_list = processed_symptoms
    
    # Initialize scores with more sophisticated weighting
    total_scores = {}
    matched_symptoms = {}
    
    # Generate embeddings for all input symptoms at once for efficiency
    input_embeddings = embedding_model.encode(symptom_list, convert_to_numpy=True)
    
    # For each input symptom, find most similar cataloged symptoms
    for i, symptom in enumerate(symptom_list):
        # Special handling for exact matches first
        exact_match_found = False
        
        # Check for exact or substring matches first
        for entry in medical_data:
            entry_symptoms = entry["symptoms"].split(", ")
            
            # Check for exact match or if symptom is a substring of any cataloged symptom
            for entry_symptom in entry_symptoms:
                if symptom == entry_symptom or symptom in entry_symptom:
                    # Give high score for exact/substring matches
                    score = 5.0  # Higher base score for exact matches
                    
                    if entry["disease"] in total_scores:
                        total_scores[entry["disease"]] += score
                        matched_symptoms[entry["disease"]].add(entry_symptom)
                    else:
                        total_scores[entry["disease"]] = score
                        matched_symptoms[entry["disease"]] = {entry_symptom}
                    
                    exact_match_found = True
        
        # If no exact match, use vector similarity
        if not exact_match_found:
            # Search for top 3 similar symptoms
            distances, indices = index.search(input_embeddings[i:i+1], 3)
            
            for j in range(3):  # Look at top 3 matches
                if j < len(distances[0]) and distances[0][j] < THRESHOLD:
                    matched_symptom = all_symptoms[indices[0][j]]
                    similarity_score = 1.0 / (1.0 + distances[0][j])  # Convert distance to similarity score
                    
                    # Find which diseases this symptom belongs to
                    for entry in medical_data:
                        entry_symptoms = entry["symptoms"].split(", ")
                        if matched_symptom in entry_symptoms:
                            # Weight score by symptom importance and similarity
                            score = similarity_score
                            
                            # Symptoms that appear in fewer diseases are more diagnostic - give them higher weight
                            symptom_rarity = 1.0 / sum(1 for e in medical_data if matched_symptom in e["symptoms"].split(", "))
                            score *= (1 + symptom_rarity)
                            
                            # Add to total score for this disease
                            if entry["disease"] in total_scores:
                                total_scores[entry["disease"]] += score
                                matched_symptoms[entry["disease"]].add(matched_symptom)
                            else:
                                total_scores[entry["disease"]] = score
                                matched_symptoms[entry["disease"]] = {matched_symptom}
    
    if not total_scores:
        return None
    
    # Add bonus for diseases that match a higher percentage of input symptoms
    for disease in total_scores:
        coverage = len(matched_symptoms[disease]) / len(symptom_list)
        total_scores[disease] *= (1 + coverage)
    
    # If confidence is very low, don't return a match
    best_match = max(total_scores, key=total_scores.get)
    best_score = total_scores[best_match]
    
    # Set minimum confidence threshold - lower scores are too unreliable
    MIN_CONFIDENCE = 3.0
    if best_score < MIN_CONFIDENCE:
        return None
    
    # Get the corresponding disease entry
    for entry in medical_data:
        if entry["disease"] == best_match:
            result = entry.copy()
            # Add confidence score and matched symptoms for more context
            result["confidence_score"] = round(best_score, 2)
            result["matched_symptoms"] = list(matched_symptoms[best_match])
            return result

    return None

# Simple mapping for common symptoms to their normalized form
COMMON_SYMPTOM_MAPPINGS = {
    "cold": "cold, runny nose, sneezing",
    "cough": "cough, cold",
    "headache": "headache, mild pain",
    "migraine": "severe headache, sensitivity to light",
    "fever": "fever, mild fever",
    "stomach pain": "stomach pain, abdominal discomfort",
    "diarrhea": "diarrhea, stomach pain",
    "nausea": "nausea, vomiting",
    "vomiting": "vomiting, nausea",
    "pain": "mild pain, discomfort",
    "sore throat": "sore throat, difficulty swallowing",
    "fatigue": "fatigue, tiredness",
    "body ache": "body aches, muscle pain",
    "dizzy": "dizziness, lightheadedness",
    "dizziness": "dizziness, lightheadedness",
    "breathing": "difficulty breathing",
    "breath": "shortness of breath",
    "chest pain": "chest pain",
    "rash": "red rash, skin inflammation",
    "itch": "itching",
    "eye pain": "eye pain, blurred vision"
}

# Function to expand user symptoms without relying on AI
def expand_symptoms(user_input):
    # First, do basic cleaning
    cleaned = re.sub(r'i have|suffering from|having|with', '', user_input.lower()).strip()
    cleaned = re.sub(r'[^\w\s,]', ' ', cleaned)  # Replace punctuation with spaces
    
    # Split into individual symptoms
    symptoms = [s.strip() for s in cleaned.split(',')]
    
    # Handle single symptom case without commas
    if len(symptoms) == 1 and ' ' in symptoms[0]:
        # Try splitting by spaces for multiple symptoms
        space_split = [s.strip() for s in symptoms[0].split() if len(s.strip()) > 2]
        if len(space_split) > 1:
            symptoms = space_split
    
    # Expand each symptom if we have a mapping for it
    expanded = []
    for symptom in symptoms:
        if symptom in COMMON_SYMPTOM_MAPPINGS:
            expanded.extend(COMMON_SYMPTOM_MAPPINGS[symptom].split(', '))
        else:
            expanded.append(symptom)
    
    # Remove duplicates and join back for output
    return list(set(expanded))

# Main API route
@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(request: SymptomsRequest):
    if not request.symptoms or request.symptoms.strip() == "":
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty")
    
    original_symptoms = request.symptoms
    refined_symptoms = None
    
    # Try to use AI for refinement, but have a fallback if it fails
    try:
        system_prompt = """You are a medical expert. Your task is to refine the following medical symptoms into clear, concise medical terminology.
        Be comprehensive and keep all symptoms mentioned, splitting them into a comma-separated list."""
        
        refined_symptoms = process_with_together_ai(
            request.symptoms, system_prompt
        )
    except Exception as e:
        print(f"Error with AI refinement: {e}")
    
    # If AI refinement failed, use our symptom expansion function
    if not refined_symptoms:
        expanded = expand_symptoms(original_symptoms)
        refined_symptoms = ", ".join(expanded)
    
    # Split symptoms and find the best disease
    symptom_list = [s.strip().lower() for s in refined_symptoms.split(",") if s.strip()]
    
    # Print for debugging
    print(f"Original input: '{original_symptoms}'")
    print(f"Refined to: '{refined_symptoms}'")
    print(f"Symptom list: {symptom_list}")
    
    best_match = find_best_disease(symptom_list)

    if not best_match:
        # If confidence is too low or no match, return a safe response
        return {
            "disease": "Unspecified symptoms",
            "diagnosis": "The symptoms described are not specific enough for a confident diagnosis.",
            "medicines": ["Consult a doctor before taking any medication"],
            "tests": ["Consult a healthcare provider for appropriate tests"],
            "precautions": ["Rest", "Hydration", "Consult a healthcare professional"],
            "food": ["Balanced diet", "Stay hydrated"],
            "emergency": False,
            "ai_suggestion": "Based on the symptoms provided, a specific condition could not be confidently identified. Please consult a healthcare professional for proper diagnosis.",
            "action_plan": "Visit a healthcare provider for proper evaluation of your symptoms."
        }
    else:
        # Print match details for debugging
        print(f"Matched disease: {best_match['disease']}")
        print(f"Confidence: {best_match.get('confidence_score', 'unknown')}")
        print(f"Matched symptoms: {best_match.get('matched_symptoms', [])}")
        
        response = best_match.copy()
        if best_match["emergency"]:
            response["alert"] = f"⚠️ This is a critical condition! Seek medical help immediately. {best_match.get('disease')} requires prompt medical attention."
        
        # Add more context to the response
        if "confidence_score" in best_match:
            response["diagnosis"] = f"{response['diagnosis']}. Confidence score: {best_match['confidence_score']}."
        
        if "matched_symptoms" in best_match:
            response["matched_symptoms"] = best_match["matched_symptoms"]

        # Always use our simple suggestion without relying on AI
        response["ai_suggestion"] = generate_ai_suggestion(
            response["disease"], response.get("food", []), response.get("emergency", False)
        )
        
        # Simple action plan without AI
        response["action_plan"] = f"For {response['disease']}: Take prescribed medications, follow recommended precautions, and consult a healthcare professional for personalized advice."

        return response

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}