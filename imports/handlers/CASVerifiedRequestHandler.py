#!/usr/bin/env python

import os
import sys

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

import tornado.httpserver
import tornado.ioloop
import tornado.web
import base64
import socket
import uuid
import urllib2
import xml.etree.ElementTree

from constants import SERVICE_URL, CAS_SERVER
from VerifiedHTTPSHandler import VerifiedHTTPSHandler

class CASVerifiedRequestHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
        
    def logout_user(self):
        self.clear_cookie("user")
        self.redirect(CAS_SERVER + "/cas/logout", permanent=False)
        
    def validate_user(self):
        if self.get_argument('ticket', default=None):
            #need to validate ticket
            ticket = self.get_argument('ticket')
            
            #generate URL for ticket validation 
            cas_validate = CAS_SERVER + "/cas/serviceValidate?ticket=" + ticket + "&service=" + SERVICE_URL
            https_handler = VerifiedHTTPSHandler()
            url_opener = urllib2.build_opener(https_handler)
            
            try:
                f_xml_assertion = url_opener.open(cas_validate)
            except urllib2.URLError:
                self.write("Error validating certificate of CAS server.")
                self.finish()
                return
            
            if not f_xml_assertion:
                print 'Unable to authenticate: trouble retrieving assertion from CAS to validate ticket.'
                self.send_error(status_code=401)
                return

            #parse CAS XML assertion into a ElementTree
            assertion_tree = xml.etree.ElementTree.parse(f_xml_assertion)
            if not assertion_tree:
                print 'Unable to authenticate: trouble parsing XML assertion.'
                self.send_error(status_code=401)
                return
            
            user_name = None
            #find <cas:user> in ElementTree
            for e in assertion_tree.iter():
                #print "DEBUG: Found tag '%s'" % e.tag
                if e.tag == "{http://www.yale.edu/tp/cas}user":
                    user_name = e.text
                
            #close the handle to the ticket assertion
            f_xml_assertion.close()
                
            print "Got validation: user=%s" %(user_name)
                
            if not user_name:
                #couldn't find <cas:user> in the tree
                print 'Unable to validate ticket: could not locate cas:user element.'
                self.send_error(status_code=401)
                return
                
            self.set_secure_cookie("user", user_name)
            
            self.redirect(SERVICE_URL, permanent=False)
        else:
            self.redirect(CAS_SERVER + "/cas/login?service=" + SERVICE_URL, permanent=False)
        
if __name__ == "__main__":
    class MyRequestHandler(CASVerifiedRequestHandler):
        def get(self, action):
            print "action =", action
        
            if action == "logout":
                self.logout_user()
            else:
                if self.get_current_user() is None:
                    self.validate_user()
                    return
                    
                self.write("Logged in as %s!<br><a href=\"/logout\">logout</a>" % self.get_current_user())
                self.finish()
                


    handlers = [
        (r"/(.*)", MyRequestHandler),
    ]

    #cookie_secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
    cookie_secret = "g9Usc0wTSMWxV5a7G5o5YcXPb3ftcUBwhUoFT62KJks="

    if __name__ == "__main__":
            tornado_app = tornado.web.Application(handlers, cookie_secret=cookie_secret)
            
            tornado_http = tornado.httpserver.HTTPServer(tornado_app, ssl_options= {"certfile": "misc/server.crt", "keyfile": "misc/server.key"})
            tornado_http.bind(8080, family=socket.AF_INET)
            tornado_http.start()
            tornado.ioloop.IOLoop.instance().start()
