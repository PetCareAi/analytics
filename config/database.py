import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_supabase_client() -> Client:
    """Retorna cliente do Supabase configurado."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY devem estar definidos no arquivo .env")
    
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Cliente global
supabase: Client = get_supabase_client()