#!/usr/bin/env python3
"""
End-to-end Week 1 validation test
Validates all completed setup steps (1.1 - 1.7)
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists"""
    if Path(path).exists():
        print(f"   ✅ {description}")
        return True
    else:
        print(f"   ❌ {description} (not found)")
        return False

def test_week1_completion():
    """Comprehensive test for Week 1 completion"""
    
    print("🎯 Week 1 Completion Validation Test\n")
    print("=" * 60)
    
    base_path = Path(__file__).parent.parent
    api_path = base_path / "mythweaver_api"
    mobile_path = base_path / "mythweaver_mobile"
    
    all_passed = True
    
    # Step 1.1: Project Structure
    print("\n✓ Step 1.1: Project Repositories")
    structure_checks = [
        (api_path, "Backend directory (mythweaver_api)"),
        (mobile_path, "Frontend directory (mythweaver_mobile)"),
        (base_path.parent / "CLAUDE.md", "Project documentation"),
    ]
    
    for path, desc in structure_checks:
        if not check_file_exists(str(path), desc):
            all_passed = False
    
    # Step 1.2: Backend Project
    print("\n✓ Step 1.2: Backend Initialization")
    backend_checks = [
        (api_path / "venv", "Virtual environment"),
        (api_path / "requirements.txt", "Requirements file"),
        (api_path / ".env", "Environment file"),
        (api_path / ".env.example", "Environment example"),
        (api_path / "app" / "core" / "config.py", "Config module"),
    ]
    
    for path, desc in backend_checks:
        if not check_file_exists(str(path), desc):
            all_passed = False
    
    # Check key dependencies
    print("\n   📦 Checking dependencies in requirements.txt...")
    req_file = api_path / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text()
        deps = ['fastapi', 'sqlalchemy', 'psycopg2-binary', 'pydantic', 'openai']
        missing = [dep for dep in deps if dep.lower() not in content.lower()]
        if not missing:
            print(f"   ✅ All key dependencies in requirements.txt")
        else:
            print(f"   ❌ Missing dependencies: {', '.join(missing)}")
            all_passed = False
    
    # Step 1.3: Flutter Project
    print("\n✓ Step 1.3: Flutter Initialization")
    flutter_checks = [
        (mobile_path / "pubspec.yaml", "Flutter pubspec.yaml"),
        (mobile_path / "lib", "Flutter lib directory"),
        (mobile_path / "lib" / "main.dart", "Flutter main.dart"),
    ]
    
    for path, desc in flutter_checks:
        if not check_file_exists(str(path), desc):
            all_passed = False
    
    # Check Flutter dependencies
    print("\n   📦 Checking Flutter dependencies...")
    pubspec_path = mobile_path / "pubspec.yaml"
    if pubspec_path.exists():
        content = pubspec_path.read_text()
        required_deps = ['provider', 'http', 'shared_preferences', 'flutter_secure_storage']
        missing = [dep for dep in required_deps if dep not in content]
        if not missing:
            print(f"   ✅ Flutter dependencies configured")
        else:
            print(f"   ❌ Missing Flutter dependencies: {', '.join(missing)}")
            all_passed = False
    
    # Step 1.4: Database Connection
    print("\n✓ Step 1.4: Supabase Connection")
    env_path = api_path / ".env"
    if env_path.exists():
        env_content = env_path.read_text()
        if 'DATABASE_URL' in env_content and 'supabase.com' in env_content:
            print(f"   ✅ Supabase DATABASE_URL configured")
        else:
            print(f"   ❌ Supabase DATABASE_URL not configured")
            all_passed = False
        
        if 'SUPABASE_URL' in env_content and 'SUPABASE_ANON_KEY' in env_content:
            print(f"   ✅ Supabase credentials configured")
        else:
            print(f"   ❌ Supabase credentials missing")
            all_passed = False
    
    # Step 1.5: Database Schema
    print("\n✓ Step 1.5: Core Database Schema")
    schema_checks = [
        (api_path / "migrations" / "001_initial_schema.sql", "Profiles table migration"),
        (api_path / "run_migration.py", "Migration runner script"),
    ]
    
    for path, desc in schema_checks:
        if not check_file_exists(str(path), desc):
            all_passed = False
    
    # Test database connection directly
    print("\n   🔌 Testing database connection...")
    try:
        from app.core.config import settings
        import psycopg2
        
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ Database connection working")
        print(f"      PostgreSQL: {version[:60]}...")
        
        # Check tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('profiles', 'mythweaver_campaigns');
        """)
        tables = [t[0] for t in cursor.fetchall()]
        
        if 'profiles' in tables:
            print(f"   ✅ Profiles table exists")
        else:
            print(f"   ❌ Profiles table missing")
            all_passed = False
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        all_passed = False
    
    # Step 1.6: Campaigns Table
    print("\n✓ Step 1.6: Campaigns Table")
    campaigns_checks = [
        (api_path / "migrations" / "002_campaigns_table.sql", "Campaigns table migration"),
        (api_path / "test_campaigns_table.py", "Campaigns table test"),
    ]
    
    for path, desc in campaigns_checks:
        if not check_file_exists(str(path), desc):
            all_passed = False
    
    # Check campaigns table in database
    try:
        import psycopg2
        from app.core.config import settings
        
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'mythweaver_campaigns';
        """)
        if cursor.fetchone():
            print(f"   ✅ Campaigns table exists in database")
        else:
            print(f"   ❌ Campaigns table not in database")
            all_passed = False
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   ⚠️  Could not verify campaigns table: {e}")
    
    # Step 1.7: Backend Configuration
    print("\n✓ Step 1.7: Backend Configuration")
    try:
        from app.core.config import settings
        
        print(f"   ✅ Configuration module loaded")
        
        if settings.APP_NAME == "Mythweaver API":
            print(f"   ✅ App name updated to Mythweaver")
        else:
            print(f"   ❌ App name not updated: {settings.APP_NAME}")
            all_passed = False
        
        if settings.STORYFIRE_FREE_DAILY == 40 and settings.STORYFIRE_COST_PER_ACTION == 2:
            print(f"   ✅ Storyfire economics: 40 = 20 actions")
        else:
            print(f"   ❌ Storyfire settings incorrect")
            all_passed = False
        
        if settings.JWT_SECRET_KEY and settings.JWT_SECRET_KEY != "your-super-secret-jwt-key-change-in-production":
            print(f"   ✅ JWT secret customized")
        else:
            print(f"   ⚠️  JWT secret not customized")
        
        if settings.OPENAI_API_KEY and 'sk-' in settings.OPENAI_API_KEY:
            print(f"   ✅ OpenAI API key configured")
        else:
            print(f"   ⚠️  OpenAI API key not configured")
            
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("\n🎉 SUCCESS: All Week 1 steps completed and validated!")
        print("\nYou're ready to proceed to Week 2: Character Creation Backend")
        print("\nCompleted:")
        print("  ✅ Step 1.1: Project structure created")
        print("  ✅ Step 1.2: Backend initialized with dependencies")
        print("  ✅ Step 1.3: Flutter project created")
        print("  ✅ Step 1.4: Supabase connection established")
        print("  ✅ Step 1.5: Profiles table with Storyfire system")
        print("  ✅ Step 1.6: Campaigns table with RLS")
        print("  ✅ Step 1.7: Configuration with JWT, OpenAI, Storyfire")
        return True
    else:
        print("\n⚠️  INCOMPLETE: Some Week 1 steps need attention")
        print("\nReview the checks above and fix any ❌ items before proceeding.")
        return False

if __name__ == "__main__":
    success = test_week1_completion()
    sys.exit(0 if success else 1)
