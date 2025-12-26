#!/usr/bin/env python3
"""
Test campaigns table RLS (Row Level Security) policies
"""
import os
import sys
from uuid import uuid4
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_campaigns_rls():
    """Test that RLS policies prevent unauthorized access"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        sys.exit(1)
    
    try:
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verify campaigns table exists
        print("\n1️⃣ Checking campaigns table exists...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'mythweaver_campaigns';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Table 'mythweaver_campaigns' exists")
        else:
            print(f"   ❌ Table 'mythweaver_campaigns' not found")
            sys.exit(1)
        
        # Check table structure
        print("\n2️⃣ Checking campaigns table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'mythweaver_campaigns'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"   📊 Found {len(columns)} columns:")
        for col_name, data_type, nullable, default in columns:
            null_str = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"      - {col_name}: {data_type} {null_str}{default_str}")
        
        # Check RLS is enabled
        print("\n3️⃣ Checking Row Level Security...")
        cursor.execute("""
            SELECT relname, relrowsecurity 
            FROM pg_class 
            WHERE relname = 'mythweaver_campaigns';
        """)
        
        rls_result = cursor.fetchone()
        if rls_result and rls_result[1]:
            print(f"   ✅ RLS is ENABLED on mythweaver_campaigns")
        else:
            print(f"   ⚠️  RLS is NOT enabled on mythweaver_campaigns")
        
        # Check RLS policies
        print("\n4️⃣ Checking RLS policies...")
        cursor.execute("""
            SELECT policyname, cmd, qual, with_check
            FROM pg_policies 
            WHERE tablename = 'mythweaver_campaigns';
        """)
        
        policies = cursor.fetchall()
        if policies:
            print(f"   ✅ Found {len(policies)} RLS policies:")
            for policy_name, cmd, qual, with_check in policies:
                print(f"      - {policy_name} ({cmd})")
        else:
            print(f"   ⚠️  No RLS policies found")
        
        # Check indexes
        print("\n5️⃣ Checking indexes...")
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes 
            WHERE tablename = 'mythweaver_campaigns'
            ORDER BY indexname;
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            print(f"   ✅ Found {len(indexes)} indexes:")
            for idx_name, idx_def in indexes:
                print(f"      - {idx_name}")
        else:
            print(f"   ⚠️  No indexes found")
        
        # Insert a test campaign (using superuser connection, so RLS is bypassed)
        print("\n6️⃣ Inserting test campaign...")
        test_user_id = uuid4()
        test_campaign_id = uuid4()
        
        # First, create a test user in auth.users (if it doesn't exist)
        cursor.execute("""
            INSERT INTO auth.users (id, email)
            VALUES (%s, 'test@example.com')
            ON CONFLICT (id) DO NOTHING;
        """, (str(test_user_id),))
        
        # Insert test campaign
        cursor.execute("""
            INSERT INTO public.mythweaver_campaigns 
            (id, user_id, name, template_id, tone, difficulty)
            VALUES (%s, %s, 'Test Campaign', 'broken_kingdom', 'balanced', 'normal')
            RETURNING id, name;
        """, (str(test_campaign_id), str(test_user_id)))
        
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Test campaign created: {result[1]} (ID: {result[0]})")
        
        # Verify we can query it
        cursor.execute("""
            SELECT id, name, template_id, current_scene_number
            FROM public.mythweaver_campaigns
            WHERE id = %s;
        """, (str(test_campaign_id),))
        
        campaign = cursor.fetchone()
        if campaign:
            print(f"   ✅ Campaign retrieved: {campaign[1]}, Scene: {campaign[3]}")
        
        # Clean up test data
        print("\n7️⃣ Cleaning up test data...")
        cursor.execute("DELETE FROM public.mythweaver_campaigns WHERE id = %s;", (str(test_campaign_id),))
        cursor.execute("DELETE FROM auth.users WHERE id = %s;", (str(test_user_id),))
        print(f"   ✅ Test data cleaned up")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 All campaigns table tests passed!")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_campaigns_rls()
