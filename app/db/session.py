"""
Database connection and session management.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Create database if not exists
url_obj = make_url(settings.DATABASE_URL)
database_name = url_obj.database

if url_obj.get_backend_name() == "mysql" and database_name:
    server_url = url_obj.set(database=None)
    server_url_str = server_url.render_as_string(hide_password=False)
    temp_engine = create_engine(server_url_str, pool_pre_ping=True)
    try:
        with temp_engine.connect() as conn:
            conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
            conn.commit()
    except Exception as e:
        print(f"Database creation warning: {e}")
    finally:
        temp_engine.dispose()

# Create main engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()