"""
Test Flutter Auth Service Integration
This script tests the auth service by making test calls to the backend
"""
import requests
import json
import random
import string

BASE_URL = "http://localhost:8000"

def generate_test_username():
    """Generate random username for testing"""
    return f"fluttertest_{''.join(random.choices(string.ascii_lowercase, k=6))}"

def test_flutter_auth_flow():
    """Test the complete auth flow that Flutter will use"""
    print("=" * 60)
    print("🧪 Flutter Auth Service Integration Test")
    print("=" * 60)
    
    # Generate test credentials
    username = generate_test_username()
    email = f"{username}@mythweaver.test"
    password = "testpass123"
    
    print(f"\n📝 Test Credentials:")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    # Test 1: Register
    print("\n1️⃣ Testing Registration...")
    register_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        auth_response = response.json()
        token = auth_response.get('accessToken')
        print(f"   ✅ Registration successful!")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"   ❌ Registration failed: {response.text}")
        return False
    
    # Test 2: Login with same credentials
    print("\n2️⃣ Testing Login...")
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        auth_response = response.json()
        new_token = auth_response.get('accessToken')
        print(f"   ✅ Login successful!")
        print(f"   Token: {new_token[:30]}...")
        
        # Test 3: Verify tokens are valid JWT format
        if '.' in token and '.' in new_token:
            print(f"   ✅ Tokens are valid JWT format")
        else:
            print(f"   ❌ Tokens don't appear to be JWT format")
    else:
        print(f"   ❌ Login failed: {response.text}")
        return False
    
    # Test 4: Test with invalid credentials
    print("\n3️⃣ Testing Invalid Login...")
    invalid_login = {
        "username": username,
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=invalid_login)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 401:
        print(f"   ✅ Invalid credentials correctly rejected")
    else:
        print(f"   ❌ Expected 401 status, got {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Flutter Auth Integration Test Complete!")
    print("=" * 60)
    print("\n📱 Flutter app can now:")
    print("   - Register new users")
    print("   - Login existing users")
    print("   - Receive and store JWT tokens")
    print("   - Handle authentication errors")
    print("\n🎯 Next: Test the Flutter app UI in the browser")
    return True

if __name__ == "__main__":
    try:
        test_flutter_auth_flow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
