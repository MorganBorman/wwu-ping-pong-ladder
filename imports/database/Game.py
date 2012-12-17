from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, BigInteger, Date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from Base import Base
from SessionFactory import SessionFactory

from Match import Match

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, Sequence('games_id_seq'), primary_key=True)
    
    match_id = Column(Integer, ForeignKey('matches.id'))
    match = relationship("Match", backref=backref('games', order_by=id))
    
    #scores = relationship("Score", backref="game")
    
    def __init__(self, match):
        self.match = match
