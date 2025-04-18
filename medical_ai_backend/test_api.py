import requests
import json

def test_health():
    response = requests.get("http://127.0.0.1:8000/health")
    print("Health check response:", response.status_code)
    print(response.json())
    
def test_diagnose():
    data = {"symptoms": "fever, cough, headache"}
    response = requests.post("http://127.0.0.1:8000/diagnose", json=data)
    print("Diagnose response status:", response.status_code)
    if response.status_code == 200:
        print("Success! Diagnosis:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error response:", response.text)

if __name__ == "__main__":
    print("Testing the Medical AI API...")
    test_health()
    print("\nTesting diagnosis endpoint...")
    test_diagnose() 