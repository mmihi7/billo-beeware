from billo.config.supabase import supabase_config

def test_supabase():
    try:
        client = supabase_config.get_client()
        print("✅ Supabase client initialized successfully!")
        
        # Test a simple query
        response = client.table('profiles').select('*').limit(1).execute()
        if hasattr(response, 'data'):
            print("✅ Successfully queried profiles table")
            print(f"Found {len(response.data)} profiles")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_supabase()