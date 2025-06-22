#!/usr/bin/env python3
"""
Test script for the complete NLQ to Natural Language Response flow
"""

import requests
import json
import os

def test_complete_flow():
    """Test the complete flow from NLQ to natural language response"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/query"
    
    # Test data
    test_questions = [
        {
            "question": "How many users do we have?",
            "tenant_id": "tenant_123"
        }
    ]
    
    print("🚀 Testing Complete NLQ to Natural Language Response Flow")
    print("=" * 60)
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {test_case['question']}")
        print("-" * 40)
        
        try:
            # Make API request
            response = requests.post(url, json=test_case, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Success!")
                print(f"   Question: {result['question']}")
                print(f"   SQL Generated: {result['sql_query']}")
                print(f"   Natural Language Response: {result['natural_language_response']}")
                print(f"   Data Rows: {result['row_count']}")
                
                if result.get('data'):
                    print(f"   Sample Data: {result['data'][:2]}")  # Show first 2 rows
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n🎉 Testing completed!")

def test_health_endpoints():
    """Test health check endpoint"""
    
    print("\n🏥 Testing Health Endpoints")
    print("=" * 40)
    
    # Test main health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Main health endpoint: OK")
        else:
            print(f"❌ Main health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Main health endpoint failed: {e}")

if __name__ == "__main__":
    print("🔍 SaaS Product Usage Data Assistant - Complete Flow Test")
    print("=" * 70)
    
    # Check if API server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server returned error status")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ API server is not running. Please start it first:")
        print("   cd api_server && python main.py")
        exit(1)
    
    # Test health endpoint
    test_health_endpoints()
    
    # Test complete flow
    test_complete_flow() 