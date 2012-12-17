from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from Base import Base
from SessionFactory import SessionFactory

from User import User
from Match import Match

class TrueSkillCache(Base):
    __tablename__ = 'true_skill_cache'

    id = Column(Integer, Sequence('true_skill_cache_id_seq'), primary_key=True)
    
    match_id = Column(Integer, ForeignKey('matches.id'))
    match = relationship("Match", backref=backref('true_skill_ratings', order_by=id))
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref=backref('true_skill_ratings', order_by=id))
    
    sigma = Column(Float)
    mu = Column(Float)
    exposure = Column(Float)

    def __init__(self, sigma, mu, exposure):
        self.sigma = sigma
        self.mu = mu
        self.exposure = exposure
