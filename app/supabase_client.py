from supabase import create_client
import os

# Claves de tu Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fdujitwtuecibozsxytk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_secret_dIPA5z6gkzPG7C7O3Pb_RA_Q80ojOOX")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
