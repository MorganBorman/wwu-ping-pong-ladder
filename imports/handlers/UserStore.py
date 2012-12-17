from CASVerifiedRequestHandler import CASVerifiedRequestHandler
import json
import re

from sqlalchemy.sql.expression import desc, asc, label
from sqlalchemy import func

from database.SessionFactory import SessionFactory

from database.User import User

import constants

from resultdict import resultdict

def get_leaderboard_query(session):
    return session.query( User.id, User.displayname ).filter(User.displayname != None)

sorting_expression = re.compile(r"sort\((?P<direction>[\+|\-])(?P<column>\w+)\)")
range_expression = re.compile(r"items=(?P<lower>\d+)-(?P<upper>\d+)")

class UserStore(CASVerifiedRequestHandler):
    def get(self, user_id):
        username = self.get_current_user()
        
        if username is None:
            self.validate_user()
            return
            
        user = User.get_user(username)
                
        if user.permission_level < constants.PERMISSION_LEVEL_USER:
            self.render("denied.html", user=user)
            return
    
    
        if user_id is not None and user_id != "":
            # single item
            user_id = int(user_id)
            
            session = SessionFactory()
            try:
                result = get_leaderboard_query(session).filter(User.id == user_id).one()
                        
                result = resultdict(result)
                
                data = "{}&& "+json.dumps(result)
                self.set_header('Content-length', len(data))
                self.set_header('Content-type', 'application/json')
                self.write(data)
            finally:
                session.close()
        else:
            # query items
            
            raw_range = self.request.headers.get('Range', '')
            m = range_expression.match(raw_range)

            if m is not None:
                start = int(m.group('lower'))
                stop = int(m.group('upper')) + 1
            else:
                start = 0
                stop = -1

            raw_query = self.request.query
            m = sorting_expression.match(raw_query)
            
            if m is not None:
                    direction = m.group('direction')
                    column = m.group('column')
            else:
                    direction = '-'
                    column = "displayname"
                    
            if column not in ["id", "displayname"]:
                column = "displayname"

            if direction == '-':
                    direction = desc
            else:
                    direction = asc
            
            session = SessionFactory()
            try:
                query = get_leaderboard_query(session)
                
                filterable_columns = {'displayname': User.displayname}
                
                for col, val in self.request.arguments.iteritems():
                    if col in filterable_columns.keys():
                        val = val[0].replace('*', '%')
                        query = query.filter(filterable_columns[col].like(val))
                        
                query = query.order_by(direction(column))
                        
                query = query.slice(start, stop)
                        
                result = query.all()
                        
                result = resultdict(result)
                
                total = len(result)
            
                data = "{}&& "+json.dumps(result)
                self.set_header('Content-range', 'items {}-{}/{}'.format(start, stop, total))
                self.set_header('Content-length', len(data))
                self.set_header('Content-type', 'application/json')
                self.write(data)
                
            finally:
                session.close()

