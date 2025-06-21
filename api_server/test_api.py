#!/usr/bin/env python3
import requests
import json

def test_api():
    """Test the NLQ to SQL API endpoint"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/query"
    
    # Test data
    payload = {
        "question": "How many users signed up last month?",
        "tenant_id": "tenant_123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing API endpoint...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("-" * 50)
        
        # Make the request
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Question: {result.get('question')}")
            print(f"SQL Query: {result.get('sql_query')}")
            print(f"Explanation: {result.get('explanation')}")
            print(f"Tenant ID: {result.get('tenant_id')}")
        else:
            print("❌ ERROR!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_api() 