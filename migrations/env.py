from alembic import context
from app_fastapi.database import engine, Base, DB_URI
from app_fastapi.models import *

target_metadata = Base.metadata

def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()