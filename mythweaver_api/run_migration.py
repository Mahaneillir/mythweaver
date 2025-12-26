#!/usr/bin/env python3
"""
Run SQL migration against Supabase database
"""
import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration(migration_file: str):
    """Run a SQL migration file against the database"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        sys.exit(1)
    
    # Read migration file
    migration_path = Path(migration_file)
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    
    print(f"📄 Reading migration: {migration_path.name}")
    sql = migration_path.read_text()
    
    # Connect to database and run migration
    try:
        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print(f"🚀 Running migration: {migration_path.name}")
        cursor.execute(sql)
        
        # Commit the transaction
        conn.commit()
        print(f"✅ Migration completed successfully!")
        
        # Verify profiles table was created
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'profiles'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        if columns:
            print(f"\n📊 Profiles table structure:")
            for table, column, dtype in columns:
                print(f"   - {column}: {dtype}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migration_file = "migrations/001_initial_schema.sql"
    
    if len(sys.argv) > 1:
        migration_file = sys.argv[1]
    
    run_migration(migration_file)
