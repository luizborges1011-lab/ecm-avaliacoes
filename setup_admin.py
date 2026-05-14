"""
Run once to create the 'usuarios' table in Supabase.

Usage:
    python setup_admin.py

After running, create users via Configurações > Gerenciar Usuários in the app.
Requires SUPABASE_URL and SUPABASE_SERVICE_KEY in .env.
"""
import os
import sys
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

    print()
    print("Done. Create users via Configurações > Gerenciar Usuários in the app.")


if __name__ == "__main__":
    main()
