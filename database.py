import os
from fastapi.params import Depends
from sqlmodel import create_engine, Session
from typing import Annotated
from dotenv import load_dotenv


load_dotenv()

DB_USER= os.getenv('DB_USER')
DB_HOST= os.getenv('DB_HOST')
DB_PORT= os.getenv('DB_PORT')
DB_PASSWORD= os.getenv('DB_PASSWORD')
DB_DATABASE= os.getenv('DB_DATABASE')

database_url = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

engine = create_engine(database_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]