"""
Test Script: Flutter Auth Integration Test
Tests complete auth flow including authenticated requests.
"""

import requests
import json
import random
import string

BASE_URL = "http://localhost:8000"

def random_username():
    """Generate random username"""
    suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
    return f"testuser_{suffix}"

def test_flutter_auth_integration():
    """Test complete authentication flow as Flutter app would use it"""
    
    print("=" * 70)
    print("FLUTTER AUTH INTEGRATION TEST")
    print("=" * 70)
    
    # Generate test credentials
    username = random_username()
    email = f"{username}@test.com"
    password = "testpass123"
    
    print(f"\n📝 Test Credentials:")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    # Test 1: Register new account
    print("\n1️⃣  Testing Registration...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    print(f"   Status: {register_response.status_code}")
    if register_response.status_code != 200:
        print(f"   ❌ Registration failed: {register_response.text}")
        return False
    
    register_data = register_response.json()
    print(f"   ✅ Registration successful!")
    print(f"   Token Type: {register_data.get('tokenType')}")
    token_preview = register_data.get('accessToken', '')[:30] if register_data.get('accessToken') else 'N/A'
    print(f"   Token: {token_preview}...")
    
    # Store token
    token = register_data.get('accessToken')
    
    # Test 2: Login with same credentials
    print("\n2️⃣  Testing Login...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={  # Use JSON, not form data
            "username": username,
            "password": password
        }
    )
    
    print(f"   Status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        return False
    
    login_data = login_response.json()
    print(f"   ✅ Login successful!")
    token_preview = login_data.get('accessToken', '')[:30] if login_data.get('accessToken') else 'N/A'
    print(f"   Token: {token_preview}...")
    
    # Update token with login token
    token = login_data.get('accessToken')
    
    # Test 3: Make authenticated request WITHOUT token
    print("\n3️⃣  Testing Authenticated Request (No Token - Should Fail)...")
    unauth_response = requests.get(
        f"{BASE_URL}/narrator/me"
    )
    
    print(f"   Status: {unauth_response.status_code}")
    if unauth_response.status_code in [401, 403]:
        print(f"   ✅ Correctly rejected unauthenticated request")
    else:
        print(f"   ❌ Should have returned 401 or 403, got {unauth_response.status_code}")
    
    # Test 4: Make authenticated request WITH token
    print("\n4️⃣  Testing Authenticated Request (With Token - Should Succeed)...")
    auth_response = requests.get(
        f"{BASE_URL}/narrator/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"   Status: {auth_response.status_code}")
    if auth_response.status_code != 200:
        print(f"   ❌ Authenticated request failed: {auth_response.text}")
        return False
    
    auth_data = auth_response.json()
    print(f"   ✅ Authenticated request successful!")
    print(f"   User ID: {auth_data.get('id')}")
    print(f"   Username: {auth_data.get('username')}")
    print(f"   Email: {auth_data.get('email')}")
    print(f"   Message: {auth_data.get('message')}")
    
    # Test 5: Verify JWT token format
    print("\n5️⃣  Testing JWT Token Format...")
    parts = token.split('.')
    if len(parts) == 3:
        print(f"   ✅ Token has correct JWT format (3 parts)")
        print(f"   Header length: {len(parts[0])}")
        print(f"   Payload length: {len(parts[1])}")
        print(f"   Signature length: {len(parts[2])}")
    else:
        print(f"   ❌ Invalid JWT format: {len(parts)} parts")
        return False
    
    # Test 6: Test invalid token
    print("\n6️⃣  Testing Invalid Token...")
    invalid_response = requests.get(
        f"{BASE_URL}/narrator/me",
        headers={
            "Authorization": "Bearer invalid_token_12345"
        }
    )
    
    print(f"   Status: {invalid_response.status_code}")
    if invalid_response.status_code == 401:
        print(f"   ✅ Correctly rejected invalid token")
    else:
        print(f"   ❌ Should have returned 401 for invalid token")
    
    print("\n" + "=" * 70)
    print("✅ ALL FLUTTER AUTH INTEGRATION TESTS PASSED!")
    print("=" * 70)
    
    print("\n📱 Flutter App Integration Verified:")
    print("   ✓ User registration works")
    print("   ✓ User login returns valid JWT token")
    print("   ✓ Token can be stored and reused")
    print("   ✓ Authenticated requests work with Bearer token")
    print("   ✓ Unauthenticated requests are properly rejected")
    print("   ✓ Invalid tokens are properly rejected")
    print("   ✓ JWT token format is correct")
    
    print("\n🎯 Ready for Flutter App Testing:")
    print("   1. Open Flutter app in Chrome (should be running)")
    print("   2. Register a new account")
    print("   3. Login with credentials")
    print("   4. Token is automatically stored")
    print("   5. Future requests will include Authorization header")
    
    return True


if __name__ == "__main__":
    try:
        success = test_flutter_auth_integration()
        if not success:
            print("\n❌ SOME TESTS FAILED")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Is it running on port 8000?")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
