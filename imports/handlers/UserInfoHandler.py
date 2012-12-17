from CASVerifiedRequestHandler import CASVerifiedRequestHandler

import constants

from database.User import User

class UserInfoHandler(CASVerifiedRequestHandler):
    def get(self, uid=None):
        username = self.get_current_user()
        
        if username is None:
            self.validate_user()
            return
            
        user = User.get_user(username)
                
        if user.permission_level < constants.PERMISSION_LEVEL_USER:
            self.render("denied.html", user=user)
            return
        
        if uid is None:
            self.render("leaderboard.html", user=user)
            
        else:
            target_user = User.by_id(int(uid))
            
            self.render("user-details.html", user=user, target_user=target_user)
