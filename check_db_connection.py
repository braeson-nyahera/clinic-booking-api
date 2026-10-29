import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing from .env")

engine = create_engine(database_url, pool_pre_ping=True)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), version()")
        )
        database_name, version = result.one()

        print(f"Connected successfully to: {database_name}")
        print(f"PostgreSQL version: {version}")

finally:
    engine.dispose()