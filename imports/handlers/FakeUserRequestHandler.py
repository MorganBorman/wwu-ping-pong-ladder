import tornado.web
import constants

class FakeUserRequestHandler(tornado.web.RequestHandler):
    def get(self, username):
        self.set_secure_cookie("user", username)
        self.redirect(constants.SERVICE_URL, permanent=False)
