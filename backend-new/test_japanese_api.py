#!/usr/bin/env python3
"""
Simple test script to verify Japanese learning API endpoints are working.
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001"

def test_api_endpoints():
    """Test Japanese learning API endpoints."""
    
    print("🚀 Testing Japanese Learning API Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to server: {e}")
        return False
    
    # Test API docs endpoint
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs endpoint working")
        else:
            print(f"⚠️  API docs response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  API docs error: {e}")
    
    # Test Japanese sentences endpoint (no auth required for GET)
    try:
        response = requests.get(f"{BASE_URL}/api/v1/sentences?page=1&items_per_page=5", timeout=5)
        print(f"📚 Japanese sentences endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('data', []))} sentences")
            print("✅ Japanese sentences API working")
        elif response.status_code == 404:
            print("   (No sentences found - expected for new database)")
        else:
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Japanese sentences endpoint error: {e}")
    
    print("=" * 50)
    print("🎉 API testing completed!")
    return True

if __name__ == "__main__":
    test_api_endpoints()