from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pop1.config import DB_DSN

engine = create_engine(DB_DSN, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
