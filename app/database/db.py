from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from sqlalchemy import func, create_engine

from datetime import datetime

from app.config.cfg import settings

# ==================================================================================================

class Base(DeclarativeBase) :
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

# ==================================================================================================

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ==================================================================================================

def init_db():
    Base.metadata.create_all(bind=engine)

# ==================================================================================================

def get_db():
    with SessionLocal() as s:
        yield s

SessionDep = Annotated[Session, Depends(get_db)]