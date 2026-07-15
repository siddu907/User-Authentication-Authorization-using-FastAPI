from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = "sqlite:///./task_manager.db"

engine = create_engine(

    DATABASE_URL,

    connect_args={
        "check_same_thread": False
    },
    echo=False

)

SessionLocal = sessionmaker(

    bind=engine,

    autocommit=False,

    autoflush=False,

    expire_on_commit=False

)
class Base(DeclarativeBase):
    pass

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()