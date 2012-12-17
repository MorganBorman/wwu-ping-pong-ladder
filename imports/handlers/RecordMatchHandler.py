from CASVerifiedRequestHandler import CASVerifiedRequestHandler

import constants

from database.User import User
from database.create_match import create_match
from database.SessionFactory import SessionFactory

import datetime
import json

class RecordMatchHandler(CASVerifiedRequestHandler):
    def result(self, outcome, message):
        data = json.dumps({'type': outcome, 'msg': message})
        self.finish(data)
    
    def get(self):
        username = self.get_current_user()
        
        if username is None:
            self.validate_user()
            return
            
        user = User.get_user(username)
                
        if user.permission_level < constants.PERMISSION_LEVEL_USER:
            self.render("denied.html", user=user)
            return
        
        self.render("record-match.html", user=user)
        
    def post(self):
        username = self.get_current_user()
        
        if username is None:
            self.result("error", "Access denied.")
            return
            
        user = User.get_user(username)
                
        if user.permission_level < constants.PERMISSION_LEVEL_USER:
            self.result("error", "Access denied.")
            return
        
        try:
            user1_id = int(self.get_argument("userSelect1"))
            user2_id = int(self.get_argument("userSelect2"))
            date_time = self.get_argument("date") + " " + self.get_argument("time")
            
            games = []
            for gnum in range(3):
                game = (int(self.get_argument("score_g{}_p0".format(gnum))), int(self.get_argument("score_g{}_p1".format(gnum))))
                games.append(game)
        except:
            self.result("error", "Invalid arguments. Check that all fields are filled out correctly.")
            return
        
        if user1_id == user2_id:
            self.result("error", "Opponents must be different users.")
            return
        
        session = SessionFactory()
        try:
            user1 = session.query(User).filter(User.id == user1_id).one()
            user2 = session.query(User).filter(User.id == user2_id).one()
            
            d = datetime.datetime.strptime(date_time, "%Y-%m-%d T%H:%M:%S")
            seconds = int(d.strftime('%s'))
            
            # filter out any games which have negative or all-zero scores
            games = filter(lambda g: all(map(lambda s: s >= 0, g)) and any(map(lambda s: s > 0, g)), games)
            
            if len(games) < 2:
                self.result("error", "A match consists of two or more games.")
                return
                
            match = create_match(session, user1, user2, seconds, games)
            session.commit()
            
            self.result("success", "Match recorded successfully.")
            
        finally:
            session.close()
