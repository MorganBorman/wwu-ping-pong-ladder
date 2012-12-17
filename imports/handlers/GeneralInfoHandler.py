from CASVerifiedRequestHandler import CASVerifiedRequestHandler

import constants

from database.User import User
from database.Match import Match
from database.SessionFactory import SessionFactory

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

class GeneralInfoHandler(CASVerifiedRequestHandler):
    def get(self, mid=None):
        username = self.get_current_user()
        
        if username is None:
            self.validate_user()
            return
            
        user = User.get_user(username)
                
        if user.permission_level < constants.PERMISSION_LEVEL_USER:
            self.render("denied.html", user=user)
            return
        
        if mid is None:
            self.render("match-history.html", user=user)
        else:
            session = SessionFactory()
            try:
                target_match = session.query(Match).filter(Match.id==str(mid)).one()
                self.render("match-details.html", user=user, target_match=target_match)
            except NoResultFound:
                return None
            finally:
                session.close()
            
            
