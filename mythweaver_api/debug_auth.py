#!/usr/bin/env python3
"""
Debug script to test auth components in isolation
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, '/app')

async def test_auth_components():
    print("🔍 Testing Auth Components...")
    
    try:
        # Test imports
        print("1. Testing imports...")
        from app.utils.auth import verify_password, get_password_hash
        print("   ✅ Auth utilities imported successfully")
        
        from app.schemas.auth import UserLogin
        print("   ✅ Auth schemas imported successfully")
        
        # Test password hashing
        print("2. Testing password hashing...")
        test_password = "testpass123"
        hashed = get_password_hash(test_password)
        print(f"   ✅ Password hashed: {hashed[:20]}...")
        
        # Test password verification
        print("3. Testing password verification...")
        is_valid = verify_password(test_password, hashed)
        print(f"   ✅ Password verification: {is_valid}")
        
        # Test schema validation
        print("4. Testing schema validation...")
        login_data = UserLogin(username="testuser", password="testpass")
        print(f"   ✅ Schema validation: {login_data.username}")
        
        # Test database connection
        print("5. Testing database connection...")
        from app.core.database import get_db, engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"   ✅ Database test: {row}")
            
        print("\n🎉 All auth components working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error in auth component: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_components())