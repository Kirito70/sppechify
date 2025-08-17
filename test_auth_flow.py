#!/usr/bin/env python3
"""
Test authentication flow to debug /me endpoint issue
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_auth_flow():
    print("🔍 Testing Authentication Flow")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Login
    print("\n1. Testing Login...")
    login_data = {
        'username': 'admin',  # Assuming we have an admin user
        'password': 'admin123'  # Assuming this is the password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f"Login Response Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f"✅ Login successful! Token: {access_token[:20]}...")
            
            # Test 2: Call /me endpoint
            print("\n2. Testing /user/me/ endpoint...")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            me_response = requests.get(f"{BASE_URL}/user/me/", headers=headers)
            print(f"/me Response Status: {me_response.status_code}")
            print(f"/me Response: {me_response.text}")
            
            if me_response.status_code == 200:
                print("✅ /me endpoint working correctly!")
            else:
                print("❌ /me endpoint failed")
                print(f"Error: {me_response.text}")
        else:
            print("❌ Login failed")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on port 8001?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auth_flow()