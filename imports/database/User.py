from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, BigInteger, String, Boolean

from sqlalchemy.orm import relationship

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from Base import Base
from SessionFactory import SessionFactory

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('users_id_seq'), primary_key=True)
    permission_level = Column(Integer)
    
    username = Column(String(64), nullable=False, unique=True)
    displayname = Column(String(64), nullable=True, unique=False)
    email = Column(String(64), nullable=True, unique=True)
    showemail = Column(Boolean, default=False)
    
    #participations = relationship("Participation", backref="user")
    #scores = relationship("Score", backref="user")
    #true_skill_ratings = relationship("TrueSkillCache", backref="user")
    
    @staticmethod
    def by_id(uid):
        session = SessionFactory()
        try:
            return session.query(User).filter(User.id==uid).one()
        except NoResultFound:
            return None
        finally:
            session.close()
    
    @staticmethod
    def get_user(username):
        session = SessionFactory()
        try:
            user = session.query(User).filter_by(username=username).one()
            return user
        except NoResultFound:
            user = User(username)
            user.displayname = username
            user.email = "{}@students.wwu.edu".format(username)
            session.add(user)
            session.commit()
            print "Created new user entry in the database for user '{}'.".format(username)
        finally:
            session.close()
            
        # If the entry for the user was just created then retreive the committed version
        session = SessionFactory()
        try:
            user = session.query(User).filter_by(username=username).one()
            return user
        except NoResultFound:
            return None
        finally:
            session.close()

    def __init__(self, username, permission_level=0):
        self.username = username
        self.permission_level = permission_level

    def __repr__(self):
        return "<User('%s', '%d')>" % (self.username, self.permission_level)
