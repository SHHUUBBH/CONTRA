import requests
import json

def test_generate_api(topic):
    url = "http://localhost:5000/api/generate"
    payload = {
        "topic": topic,
        "tone": "informative",
        "variants": 1
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"Testing topic: {topic}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"API Response: {json.dumps(result, indent=2)[:500]}...")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test with topics that work and don't work
    test_generate_api("malaria")
    print("\n" + "-"*50 + "\n")
    test_generate_api("mahabharat") 