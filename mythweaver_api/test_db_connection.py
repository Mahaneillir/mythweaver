"""
Test script to verify database connection to Supabase
Run this script to ensure your DATABASE_URL is configured correctly
"""
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

print("🔍 Testing database connection...")
print(f"📍 URL: {DATABASE_URL[:30]}...{DATABASE_URL[-30:]}")  # Hide sensitive middle part

def test_connection():
    try:
        # Parse the DATABASE_URL
        result = urlparse(DATABASE_URL)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        # Connect to the database
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Test connection with a simple query
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        
        print("✅ Database connection successful!")
        print(f"📊 PostgreSQL version: {version[:50]}...")
        
        # Test if we can query the auth schema
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'auth'")
        auth_tables = cur.fetchone()[0]
        print(f"🔐 Auth schema tables found: {auth_tables}")
        
        # Check if profiles table exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'profiles')")
        profiles_exists = cur.fetchone()[0]
        
        if profiles_exists:
            print("✅ 'profiles' table exists")
        else:
            print("⚠️  'profiles' table not found - will be created in next step")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
        print("\n🎉 All database checks passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check your DATABASE_URL password in .env file")
        print("   2. Verify your Supabase project is active")
        print("   3. Check if your IP is allowed in Supabase (Project Settings → Database → Connection Pooling)")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
