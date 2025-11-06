# SQLAlchemy engine factory + health check

"""Database engine creation and health check utilities."""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ..config import SQLALCHEMY_DATABASE_URI

# Global engine instance
_engine_instance: Engine | None = None


def get_engine() -> Engine:
    """Get the global database engine instance, creating it if necessary."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = create_db_engine()
    return _engine_instance


def create_db_engine(database_uri: str = None) -> Engine:
    """Create and configure the SQLAlchemy database engine."""
    if database_uri is None:
        database_uri = SQLALCHEMY_DATABASE_URI

    engine = create_engine(database_uri, future=True)
    return engine


def test_db_connection(engine: Engine = None) -> list[str]:
    """Test the database connection and return list of table names."""
    if engine is None:
        engine = get_engine()

    # Test the connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Connected successfully! Found tables: {tables}")
        return tables
