import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import metadata, star_mappers


@pytest.fixture()
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.drop_all(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture()
def session(in_memory_db):
    star_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
