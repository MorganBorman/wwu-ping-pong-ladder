from CASVerifiedRequestHandler import CASVerifiedRequestHandler

import constants

from database.User import User
from database.SessionFactory import SessionFactory

import json

from strip_tags import strip_tags

class UserSettingsHandler(CASVerifiedRequestHandler):
    def result(self, outcome, message, user=None):
        data = {'type': outcome, 'msg': message}
        if user is not None:
            data['user'] = {'id': user.id, 'displayname': user.displayname, 'email': user.email, 'showemail': user.showemail}
        data = json.dumps(data)
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
        
        self.render("user-settings.html", user=user)
        
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
            displayname = strip_tags(self.get_argument("displayname"))
            email = strip_tags(self.get_argument("email"))
            showemail = bool(self.get_argument("showemail", False))
        except:
            self.result("error", "Invalid arguments. Check that all fields are filled out correctly.")
            return
        
        session = SessionFactory()
        try:
            user.displayname = displayname
            user.email = email
            user.showemail = showemail
            session.add(user)
            session.commit()
            self.result("success", "Settings saved successfully.", user)
        finally:
            session.close()
