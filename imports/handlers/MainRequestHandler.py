from CASVerifiedRequestHandler import CASVerifiedRequestHandler

import constants

from database.User import User

class MainRequestHandler(CASVerifiedRequestHandler):
    def get(self, action):
        if action == "logout":
            self.logout_user()
        elif action == "login":
            if self.get_current_user() is None:
                self.validate_user()
                return
            else:
                self.redirect("/Leaderboard", permanent=False)
                return
        else: # action == "admin":
            username = self.get_current_user()
            
            if username is None:
                self.validate_user()
                return
                
            user = User.get_user(username)
                    
            if user.permission_level >= constants.PERMISSION_LEVEL_ADMIN:
                #self.render("admin")
                self.finish("This will be the admin page.")
            else:
                self.render("denied.html", user=user)
