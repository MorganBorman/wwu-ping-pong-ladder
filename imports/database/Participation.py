from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, BigInteger, String, Boolean

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from Base import Base
from SessionFactory import SessionFactory

from User import User
from Match import Match

class Participation(Base):
    __tablename__ = 'participations'

    id = Column(Integer, Sequence('participations_id_seq'), primary_key=True)
    
    match_id = Column(Integer, ForeignKey('matches.id'))
    match = relationship("Match", backref=backref('participations', order_by=id))
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref=backref('participations', order_by=id))

    def __init__(self):
        pass

