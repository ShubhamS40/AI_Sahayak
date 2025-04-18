import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test the health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status: {response.status_code}")
    print(response.json())
    print("-" * 50)

def test_diagnose(symptoms, description=""):
    """Test the diagnose endpoint with given symptoms"""
    print(f"\nTesting diagnosis for: {description or symptoms}")
    
    data = {"symptoms": symptoms}
    try:
        response = requests.post(f"{BASE_URL}/diagnose", json=data, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Diagnosed as: {result['disease']}")
            print(f"📝 Diagnosis: {result['diagnosis']}")
            print(f"⚠️ Emergency: {result['emergency']}")
            
            if "confidence_score" in result:
                print(f"🎯 Confidence: {result['confidence_score']}")
                
            if "matched_symptoms" in result:
                print(f"🔍 Matched symptoms: {', '.join(result['matched_symptoms'])}")
                
            if "action_plan" in result:
                print(f"📋 Action plan preview: {result['action_plan'][:150]}...")
                
            print(f"💊 Medicines: {', '.join(result['medicines'])}")
            print(f"🍎 Food recommendations: {', '.join(result['food'])}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("-" * 50)

def run_comprehensive_tests():
    """Run a series of tests with different symptoms"""
    test_health()
    time.sleep(1)
    
    # Test common diseases with clear symptoms
    test_diagnose("fever, cough, sore throat", "Flu symptoms")
    time.sleep(1)
    
    test_diagnose("headache, fever, chills, body aches", "Typhoid symptoms")
    time.sleep(1)
    
    test_diagnose("frequent urination, excessive thirst, fatigue", "Diabetes symptoms")
    time.sleep(1)
    
    test_diagnose("jaundice, yellow eyes, dark urine", "Jaundice symptoms")
    time.sleep(1)
    
    # Test with combination of symptoms
    test_diagnose("cough, fever, headache, runny nose", "Cold or flu symptoms")
    time.sleep(1)
    
    # Test with vague symptoms
    test_diagnose("fatigue, general weakness, mild headache", "Vague symptoms")
    time.sleep(1)
    
    # Test with symptoms in different language/format
    test_diagnose("bukhar, sardard, khasi", "Hindi symptoms")

if __name__ == "__main__":
    print("🏥 TESTING IMPROVED MEDICAL AI API 🏥")
    print("=" * 50)
    run_comprehensive_tests() 