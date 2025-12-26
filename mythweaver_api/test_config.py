#!/usr/bin/env python3
"""
Test backend configuration and database connection
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def test_configuration():
    """Test that configuration is loaded correctly"""
    
    print("🔧 Testing Configuration Settings\n")
    
    # Test application settings
    print("📱 Application Settings:")
    print(f"   - App Name: {settings.APP_NAME}")
    print(f"   - Version: {settings.APP_VERSION}")
    print(f"   - Environment: {settings.ENVIRONMENT}")
    print(f"   - Debug: {settings.DEBUG}")
    
    # Test Storyfire settings (Mythweaver-specific)
    print("\n💫 Storyfire Settings:")
    print(f"   - Free Daily Storyfire: {settings.STORYFIRE_FREE_DAILY}")
    print(f"   - Cost Per Action: {settings.STORYFIRE_COST_PER_ACTION}")
    
    # Validate Storyfire economics
    actions_per_day = settings.STORYFIRE_FREE_DAILY // settings.STORYFIRE_COST_PER_ACTION
    print(f"   - Free Actions Per Day: {actions_per_day}")
    
    if settings.STORYFIRE_FREE_DAILY == 40 and settings.STORYFIRE_COST_PER_ACTION == 2:
        print("   ✅ Storyfire economics configured correctly (40 Storyfire = 20 actions)")
    else:
        print("   ⚠️  Storyfire settings don't match expected values (40/2)")
    
    # Test database settings
    print("\n🗄️  Database Settings:")
    db_url_display = settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL
    print(f"   - DATABASE_URL: {db_url_display}")
    print(f"   - Supabase URL: {settings.SUPABASE_URL}")
    
    # Test security settings
    print("\n🔐 Security Settings:")
    jwt_preview = settings.JWT_SECRET_KEY[:10] + "..." if len(settings.JWT_SECRET_KEY) > 10 else settings.JWT_SECRET_KEY
    print(f"   - JWT Secret: {jwt_preview}")
    print(f"   - JWT Algorithm: {settings.JWT_ALGORITHM}")
    print(f"   - Token Expiry: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    
    if settings.JWT_SECRET_KEY == "your-super-secret-jwt-key-change-in-production":
        print("   ⚠️  WARNING: Using default JWT secret key - change in production!")
    else:
        print("   ✅ JWT secret key has been customized")
    
    # Test AI settings
    print("\n🤖 AI Settings:")
    print(f"   - Model: {settings.MODEL_NAME}")
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-your-openai-api-key-here":
        api_key_preview = settings.OPENAI_API_KEY[:10] + "..." if len(settings.OPENAI_API_KEY) > 10 else "***"
        print(f"   - OpenAI API Key: {api_key_preview}")
        print("   ✅ OpenAI API key configured")
    else:
        print("   ⚠️  OpenAI API key not configured - AI features will not work")
    
    # Test CORS settings
    print("\n🌐 CORS Settings:")
    origins = settings.ALLOWED_ORIGINS.split(",")
    print(f"   - Allowed Origins ({len(origins)}):")
    for origin in origins:
        print(f"      • {origin}")
    
    # Test database connection
    print("\n🔌 Testing Database Connection:")
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ Connection successful!")
        print(f"   📊 PostgreSQL: {version[:50]}...")
        
        # Check for required tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('profiles', 'mythweaver_campaigns');
        """)
        
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        print(f"\n   📋 Checking required tables:")
        for table in ['profiles', 'mythweaver_campaigns']:
            if table in table_names:
                print(f"      ✅ {table}")
            else:
                print(f"      ❌ {table} (not found)")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    print("\n🎉 Configuration test completed!")
    return True

if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1)
