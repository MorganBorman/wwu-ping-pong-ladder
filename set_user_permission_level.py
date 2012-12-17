#!/usr/bin/python

import os
import sys

system_directory = os.path.dirname(os.path.abspath(__file__))

sys.path.append(system_directory + "/imports")

username = sys.argv[1]
permission_level = int(sys.argv[2])

from database.User import User
from database.SessionFactory import SessionFactory

session = SessionFactory()
try:
    user = User.get_user(username)
    user.permission_level = permission_level
    session.add(user)
    session.commit()
    print "Successfully set permission level for user '{}' to {}.".format(user.username, user.permission_level)
finally:
    session.close()

