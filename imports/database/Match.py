from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, BigInteger, Date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from Base import Base
from SessionFactory import SessionFactory

from User import User

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, Sequence('matches_id_seq'), primary_key=True)
    
    #participations = relationship("Participation", backref="match")
    #true_skill_ratings = relationship("TrueSkillCache", backref="match")
    #games = relationship("Game", backref="match")
    
    date = Column(BigInteger)
    date_recorded = Column(BigInteger)
    
    def __init__(self, date, date_recorded):
        self.date = date
        self.date_recorded = date_recorded
    
    @staticmethod
    def by_id(mid):
        session = SessionFactory()
        try:
            return session.query(Match).filter(Match.id==mid).one()
        except NoResultFound:
            return None
        finally:
            session.close()
