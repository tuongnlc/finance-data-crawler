import os

from src.shared.infrastructure.db.connection import (
    get_async_engine,
    get_async_session_factory,
)
from src.shared.infrastructure.db.models import Base


def configure_postgres_env_from_airflow_connection(conn_id: str | None) -> bool:
    if not conn_id:
        return False

    try:
        from airflow.hooks.base import BaseHook
    except ImportError:
        print("Warning: Airflow not installed, skipping connection lookup.")
        return False

    try:
        print(f"Fetching connection details for {conn_id} from Airflow...")
        conn = BaseHook.get_connection(conn_id)

        updated = False
        if conn.host:
            os.environ["POSTGRES_HOST"] = conn.host
            updated = True
        if conn.login:
            os.environ["POSTGRES_USER"] = conn.login
            updated = True
        if conn.password:
            os.environ["POSTGRES_PASSWORD"] = conn.password
            updated = True
        if conn.port:
            os.environ["POSTGRES_PORT"] = str(conn.port)
            updated = True
        if conn.schema:
            os.environ["POSTGRES_DB"] = conn.schema
            updated = True

        if updated:
            print(
                f"Updated DB config from Airflow connection: {conn.host}:{conn.port}/{conn.schema}"
            )
            get_async_engine.cache_clear()
            get_async_session_factory.cache_clear()

        return updated
    except Exception as e:
        print(f"Error fetching connection {conn_id}: {e}")
        return False


async def init_db_schema() -> None:
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
