from sqlalchemy import create_engine
from hearsay.config import sqlalchemy_url

engine = create_engine(sqlalchemy_url, echo=True, pool_pre_ping=True)
