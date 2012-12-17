from sqlalchemy import Sequence
from sqlalchemy import Column, BigInteger, Integer, Date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from Base import Base
from SessionFactory import SessionFactory

from User import User
from Game import Game

class Score(Base):
    __tablename__ = 'scores'

    id = Column(Integer, Sequence('scores_id_seq'), primary_key=True)
    
    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship("Game", backref=backref('scores', order_by=id))
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", backref=backref('scores', order_by=id))
    
    score = Column(Integer)
    
    def __init__(self, score):
        self.score = score
