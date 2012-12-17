from CASVerifiedRequestHandler import CASVerifiedRequestHandler
import json
import re

from sqlalchemy.sql.expression import desc, asc, label
from sqlalchemy import func

from database.SessionFactory import SessionFactory

from database.User import User
from database.Match import Match
from database.TrueSkillCache import TrueSkillCache

import constants

from resultdict import resultdict

def get_rankstore_query(session, user_id):
    temp = session.query( Match.date_recorded.label('timestamp'), 
                          TrueSkillCache.exposure.label('rank') ).\
                      join( TrueSkillCache ).\
                      filter( TrueSkillCache.user_id == user_id ).subquery()
                      
    return session.query( temp )

sorting_expression = re.compile(r"sort\((?P<direction>[\+|\-])(?P<column>\w+)\)")
range_expression = re.compile(r"items=(?P<lower>\d+)-(?P<upper>\d+)")

class RankStore(CASVerifiedRequestHandler):
    def get(self, user_id, timestamp):
        user_id = int(user_id)
        username = self.get_current_user()
        
        if username is None:
            self.validate_user()
            return
            
        user = User.get_user(username)
                
        if user.permission_level < constants.PERMISSION_LEVEL_USER:
            self.render("denied.html", user=user)
            return
    
    
        if timestamp is not None and timestamp != "":
            # single item
            timestamp = int(timestamp)
            
            session = SessionFactory()
            try:
                result = get_rankstore_query(session, user_id).filter_by(timestamp=timestamp).one()
                        
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
                    column = "timestamp"
                    
            if column not in ["timestamp", "rank"]:
                column = "timestamp"

            if direction == '-':
                    direction = desc
            else:
                    direction = asc
            
            session = SessionFactory()
            try:
                query = get_rankstore_query(session, user_id)
                        
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

