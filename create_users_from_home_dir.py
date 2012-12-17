#!/usr/bin/python

import os
import sys
import random

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

#from names import names as usernames
from names_from_home_directories import names as usernames

from database.User import User
from database.SessionFactory import SessionFactory

import constants

session = SessionFactory()
try:
    for username in usernames:
        permission_level = constants.PERMISSION_LEVEL_USER
        user = User(username, permission_level)
        user.displayname = username
        user.email = "{}@students.wwu.edu".format(username)
        user.showemail = False
        session.add(user)
    session.commit()
finally:
    session.close()

