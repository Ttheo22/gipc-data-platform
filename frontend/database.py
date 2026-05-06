import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# ── Database Connection ────────────────────────────────────
def get_engine():
    db_host = os.getenv("DB_HOST",     "localhost")
    db_port = os.getenv("DB_PORT",     "5432")
    db_name = os.getenv("DB_NAME",     "gipc_platform")
    db_user = os.getenv("DB_USER",     "postgres")
    db_pass = os.getenv("DB_PASSWORD", "")

    url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)


def query(sql: str, params: dict = {}) -> list[dict]:
    """
    Runs a SQL query and returns results as a list of dicts.
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]