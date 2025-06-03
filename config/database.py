# config/database.py
import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional

def get_supabase_credentials():
    """Obtém credenciais do Supabase de diferentes fontes."""
    supabase_url = None
    supabase_key = None
    
    # Método 1: Tentar via st.secrets (Streamlit Cloud)
    try:
        supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
        supabase_key = st.secrets["supabase"]["SUPABASE_ANON_KEY"]
        return supabase_url, supabase_key
    except:
        pass
    
    # Método 2: Tentar via variáveis de ambiente do sistema
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        if supabase_url and supabase_key:
            return supabase_url, supabase_key
    except:
        pass
    
    # Método 3: Tentar via arquivo .env (desenvolvimento local)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        if supabase_url and supabase_key:
            return supabase_url, supabase_key
    except:
        pass
    
    # Método 4: Valores hardcoded como fallback (apenas para desenvolvimento)
    supabase_url = "https://jthzocdiryhuytnmtekj.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp0aHpvY2RpcnlodXl0bm10ZWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgzMDA4NDUsImV4cCI6MjA2Mzg3Njg0NX0.eNbN8wZsAYz_RmcjyspXUJDPhEGYKHa4pSrWc4Hbb-M"
    
    return supabase_url, supabase_key

def get_supabase_client() -> Optional[Client]:
    """Retorna cliente do Supabase configurado."""
    try:
        supabase_url, supabase_key = get_supabase_credentials()
        
        if not supabase_url or not supabase_key:
            print("⚠️ Credenciais do Supabase não encontradas")
            return None
        
        client = create_client(supabase_url, supabase_key)
        print("✅ Cliente Supabase criado com sucesso")
        return client
        
    except Exception as e:
        print(f"❌ Erro ao criar cliente Supabase: {str(e)}")
        return None

# Variável global que será inicializada sob demanda
_supabase_client: Optional[Client] = None

def get_supabase():
    """Obtém o cliente Supabase (singleton pattern)."""
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    
    return _supabase_client

# Para compatibilidade com código existente
supabase = get_supabase()