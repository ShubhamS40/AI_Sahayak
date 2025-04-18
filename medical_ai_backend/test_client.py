import requests
import json

def test_symptom(symptom_text):
    """Test the API with a specific symptom text"""
    print(f"\n\n--------- Testing: '{symptom_text}' ---------")
    
    response = requests.post(
        "http://127.0.0.1:8000/diagnose",
        json={"symptoms": symptom_text}
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Diagnosed as: {result.get('disease', 'Unknown')}")
        print(f"Confidence score: {result.get('confidence_score', 'N/A')}")
        print(f"Matched symptoms: {', '.join(result.get('matched_symptoms', []))}")
        print(f"Medicines: {', '.join(result.get('medicines', []))}")
        if result.get('emergency'):
            print("⚠️ This is considered an EMERGENCY condition!")

if __name__ == "__main__":
    print("Testing improved symptom matching API")
    print("====================================")
    
    # Test common symptoms
    test_symptom("I have a cold")
    test_symptom("I have headache")
    test_symptom("I have cough and fever")
    test_symptom("stomach pain and nausea")
    test_symptom("sore throat with fever")
    
    # Test slightly more complex cases
    test_symptom("I've been having a bad headache and fever for 2 days")
    test_symptom("My child has a runny nose and cough")
    test_symptom("I feel dizzy and have stomach pain") 