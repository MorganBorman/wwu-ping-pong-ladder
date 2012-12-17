from sqlalchemy.orm import sessionmaker

from engine import engine

SessionFactory = sessionmaker(bind=engine)
