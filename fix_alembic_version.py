from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Update to existing migration version
    conn.execute(text("UPDATE alembic_version SET version_num = 'd1b2e25f7219'"))
    conn.commit()
    print("✅ Updated alembic version to d1b2e25f7219")

    # Verify
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    versions = list(result)
    print(f"Current version: {versions}")
