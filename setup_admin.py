"""
Run once to create the 'usuarios' table in Supabase and seed the first admin.

Usage:
    python setup_admin.py

Default admin credentials (change after first login):
    Email: luiz.h@ecm.com.br
    Senha: ECM@2026
"""
import os
import sys
import bcrypt
from dotenv import load_dotenv

load_dotenv()

SQL_CREATE = """
CREATE TABLE IF NOT EXISTS usuarios (
    id           SERIAL PRIMARY KEY,
    nome         TEXT NOT NULL,
    email        TEXT UNIQUE NOT NULL,
    senha_hash   TEXT NOT NULL,
    is_admin     BOOLEAN DEFAULT FALSE,
    ativo        BOOLEAN DEFAULT TRUE,
    atendente_nome TEXT DEFAULT '',
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
"""

SEED_USERS = [
    {"nome": "Luiz Henrique Borges", "email": "luiz.h@ecm.com.br",    "senha": "ECM@2026", "is_admin": True,  "atendente_nome": "Luiz Henrique Borges"},
    {"nome": "Bruna Madruga",        "email": "bruna@ecm.com.br",      "senha": "ECM@2026", "is_admin": False, "atendente_nome": "Bruna Madruga"},
    {"nome": "Giulia Detoni",        "email": "giulia@ecm.com.br",     "senha": "ECM@2026", "is_admin": False, "atendente_nome": "Giulia Detoni"},
    {"nome": "Franciele Favero",     "email": "franciele@ecm.com.br",  "senha": "ECM@2026", "is_admin": False, "atendente_nome": "Franciele Favero"},
    {"nome": "Simone Chenet",        "email": "simone@ecm.com.br",     "senha": "ECM@2026", "is_admin": False, "atendente_nome": "Simone Chenet"},
    {"nome": "Thais Seratto",        "email": "thais@ecm.com.br",      "senha": "ECM@2026", "is_admin": False, "atendente_nome": "Thais Seratto"},
    {"nome": "Naiara Dalmora",       "email": "naiara@ecm.com.br",     "senha": "ECM@2026", "is_admin": False, "atendente_nome": "Naiara Dalmora"},
]


def main():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        sys.exit(1)

    from supabase import create_client
    client = create_client(url, key)

    print("Creating 'usuarios' table (if not exists)...")
    try:
        client.rpc("exec_sql", {"query": SQL_CREATE}).execute()
        print("  Table created via RPC.")
    except Exception:
        print("  RPC not available — please run the following SQL in the Supabase SQL editor:")
        print(SQL_CREATE)
        print()

    print("Seeding users (skipping existing emails)...")
    for u in SEED_USERS:
        try:
            existing = client.table("usuarios").select("id").eq("email", u["email"]).execute()
            if existing.data:
                print(f"  SKIP  {u['email']} (already exists)")
                continue
            senha_hash = bcrypt.hashpw(u["senha"].encode(), bcrypt.gensalt()).decode()
            client.table("usuarios").insert({
                "nome": u["nome"],
                "email": u["email"],
                "senha_hash": senha_hash,
                "is_admin": u["is_admin"],
                "ativo": True,
                "atendente_nome": u["atendente_nome"],
            }).execute()
            role = "ADMIN" if u["is_admin"] else "atendente"
            print(f"  OK    {u['email']} ({role})")
        except Exception as e:
            print(f"  ERROR {u['email']}: {e}")

    print()
    print("Done. All users have temporary password: ECM@2026")
    print("Change passwords after first login via Configurações.")


if __name__ == "__main__":
    main()
