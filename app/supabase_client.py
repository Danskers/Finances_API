from supabase import create_client
import os

SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")


supabase = create_client(SUPABASE_KEY, SUPABASE_URL)
