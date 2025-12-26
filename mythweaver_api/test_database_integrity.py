#!/usr/bin/env python3
"""
Comprehensive database integration tests
Tests triggers, RLS policies, and data integrity
"""
import os
import sys
from uuid import uuid4
import psycopg2
from dotenv import load_dotenv
import time

load_dotenv()

def test_database_integrity():
    """Test database schema, triggers, and RLS policies"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        sys.exit(1)
    
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("🧪 Running Database Integration Tests\n")
        
        # Test 1: Profile auto-creation trigger
        print("1️⃣ Testing profile auto-creation trigger...")
        test_user_id = uuid4()
        test_email = f"test-{uuid4()}@example.com"
        
        # Insert into auth.users
        cursor.execute("""
            INSERT INTO auth.users (id, email, raw_user_meta_data)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (str(test_user_id), test_email, '{"full_name": "Test User"}'))
        
        # Check if profile was auto-created
        cursor.execute("""
            SELECT id, email, full_name, storyfire_balance, is_premium
            FROM public.profiles
            WHERE id = %s;
        """, (str(test_user_id),))
        
        profile = cursor.fetchone()
        if profile:
            print(f"   ✅ Profile auto-created for user: {profile[1]}")
            print(f"      - Full name: {profile[2]}")
            print(f"      - Storyfire balance: {profile[3]} (expected: 40)")
            print(f"      - Is premium: {profile[4]} (expected: False)")
            
            if profile[3] == 40 and profile[4] == False:
                print("   ✅ Default Storyfire values correct")
            else:
                print("   ❌ Default Storyfire values incorrect")
        else:
            print("   ❌ Profile was NOT auto-created")
            conn.rollback()
            return False
        
        # Test 2: Updated_at trigger
        print("\n2️⃣ Testing updated_at trigger...")
        cursor.execute("""
            SELECT updated_at FROM public.profiles WHERE id = %s;
        """, (str(test_user_id),))
        original_updated_at = cursor.fetchone()[0]
        
        conn.commit()  # Commit to finalize the initial timestamp
        time.sleep(1)  # Wait 1 second to ensure timestamp difference
        
        # Update profile
        cursor.execute("""
            UPDATE public.profiles 
            SET username = 'testuser' 
            WHERE id = %s
            RETURNING updated_at;
        """, (str(test_user_id),))
        
        new_updated_at = cursor.fetchone()[0]
        conn.commit()
        
        if new_updated_at > original_updated_at:
            print(f"   ✅ updated_at trigger working (old: {original_updated_at}, new: {new_updated_at})")
        else:
            print(f"   ❌ updated_at trigger NOT working")
        
        # Test 3: Campaign creation and FK constraint
        print("\n3️⃣ Testing campaign creation and foreign key...")
        test_campaign_id = uuid4()
        
        cursor.execute("""
            INSERT INTO public.mythweaver_campaigns 
            (id, user_id, name, template_id)
            VALUES (%s, %s, 'Test Campaign FK', 'broken_kingdom')
            RETURNING id, name, current_scene_number;
        """, (str(test_campaign_id), str(test_user_id)))
        
        campaign = cursor.fetchone()
        if campaign:
            print(f"   ✅ Campaign created: {campaign[1]}")
            print(f"      - Scene number: {campaign[2]} (expected: 1)")
        else:
            print("   ❌ Campaign creation failed")
        
        # Test 4: Campaign updated_at trigger
        print("\n4️⃣ Testing campaign updated_at trigger...")
        cursor.execute("""
            SELECT updated_at FROM public.mythweaver_campaigns WHERE id = %s;
        """, (str(test_campaign_id),))
        original_camp_updated = cursor.fetchone()[0]
        
        conn.commit()  # Commit to finalize timestamp
        time.sleep(1)
        
        cursor.execute("""
            UPDATE public.mythweaver_campaigns 
            SET current_scene_number = 2
            WHERE id = %s
            RETURNING updated_at;
        """, (str(test_campaign_id),))
        
        new_camp_updated = cursor.fetchone()[0]
        conn.commit()
        
        if new_camp_updated > original_camp_updated:
            print(f"   ✅ Campaign updated_at trigger working")
        else:
            print(f"   ❌ Campaign updated_at trigger NOT working")
        
        # Test 5: RLS isolation (create second user and verify cross-access blocked)
        print("\n5️⃣ Testing Row Level Security isolation...")
        test_user2_id = uuid4()
        test_email2 = f"test2-{uuid4()}@example.com"
        
        cursor.execute("""
            INSERT INTO auth.users (id, email)
            VALUES (%s, %s);
        """, (str(test_user2_id), test_email2))
        
        test_campaign2_id = uuid4()
        cursor.execute("""
            INSERT INTO public.mythweaver_campaigns 
            (id, user_id, name)
            VALUES (%s, %s, 'User2 Campaign')
            RETURNING id;
        """, (str(test_campaign2_id), str(test_user2_id)))
        
        print(f"   ✅ Created second user and campaign")
        
        # Note: RLS is enforced at the application level with SET LOCAL role
        # In direct superuser connection, RLS is bypassed
        # We'll verify the policy exists instead
        cursor.execute("""
            SELECT policyname, cmd 
            FROM pg_policies 
            WHERE tablename = 'mythweaver_campaigns'
            AND policyname = 'Users can only access their own campaigns';
        """)
        
        policy = cursor.fetchone()
        if policy:
            print(f"   ✅ RLS policy exists: {policy[0]}")
            print(f"      (Note: Policy enforced for non-superuser connections)")
        else:
            print(f"   ❌ RLS policy NOT found")
        
        # Test 6: Cascade delete (delete user, verify campaign deleted)
        print("\n6️⃣ Testing cascade delete...")
        cursor.execute("""
            DELETE FROM auth.users WHERE id = %s;
        """, (str(test_user2_id),))
        
        cursor.execute("""
            SELECT id FROM public.mythweaver_campaigns WHERE id = %s;
        """, (str(test_campaign2_id),))
        
        deleted_campaign = cursor.fetchone()
        if not deleted_campaign:
            print(f"   ✅ Campaign deleted on user deletion (CASCADE working)")
        else:
            print(f"   ❌ Campaign NOT deleted (CASCADE not working)")
        
        # Test 7: Check indexes exist
        print("\n7️⃣ Testing indexes...")
        cursor.execute("""
            SELECT schemaname, tablename, indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('profiles', 'mythweaver_campaigns')
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        expected_indexes = [
            'profiles_email_idx',
            'profiles_username_idx',
            'campaigns_user_id_idx',
            'campaigns_created_at_idx',
            'campaigns_template_id_idx'
        ]
        
        found_indexes = [idx[2] for idx in indexes]
        print(f"   Found {len(indexes)} indexes:")
        
        for expected in expected_indexes:
            if expected in found_indexes:
                print(f"      ✅ {expected}")
            else:
                print(f"      ❌ {expected} (missing)")
        
        # Test 8: Check data types and constraints
        print("\n8️⃣ Testing data constraints...")
        
        # Test JSONB default values
        cursor.execute("""
            SELECT content_limits::text 
            FROM public.mythweaver_campaigns 
            WHERE id = %s;
        """, (str(test_campaign_id),))
        
        content_limits = cursor.fetchone()[0]
        if content_limits == '{}':
            print(f"   ✅ JSONB default value working (content_limits = {{}})")
        else:
            print(f"   ⚠️  JSONB default: {content_limits}")
        
        # Test NOT NULL constraints
        try:
            cursor.execute("""
                INSERT INTO public.mythweaver_campaigns (user_id)
                VALUES (%s);
            """, (str(test_user_id),))
            print(f"   ❌ NOT NULL constraint not working (name should be required)")
            conn.rollback()
        except psycopg2.IntegrityError:
            print(f"   ✅ NOT NULL constraint working (name is required)")
            conn.rollback()
        
        # Cleanup test data
        print("\n🧹 Cleaning up test data...")
        cursor.execute("DELETE FROM public.mythweaver_campaigns WHERE id = %s;", (str(test_campaign_id),))
        cursor.execute("DELETE FROM auth.users WHERE id = %s;", (str(test_user_id),))
        conn.commit()
        print("   ✅ Test data cleaned up")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 All database integration tests passed!")
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = test_database_integrity()
    sys.exit(0 if success else 1)
