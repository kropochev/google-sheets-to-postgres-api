import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


HOST = os.environ.get('POSTGRES_HOST')
PORT = os.environ.get('POSTGRES_PORT')
USER = os.environ.get('POSTGRES_USER')
PASS = os.environ.get('POSTGRES_PASSWORD')
DB = os.environ.get('POSTGRES_DB')


SQLALCHEMY_DATABASE_URI = \
    f'postgresql://{USER}:{PASS}@{HOST}:{PORT}/{DB}'

engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
