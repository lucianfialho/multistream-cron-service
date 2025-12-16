from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        result = conn.execute(text('SELECT version_num FROM alembic_version'))
        versions = list(result)
        print(f"Current alembic version in database: {versions}")
    except Exception as e:
        print(f"Error: {e}")
