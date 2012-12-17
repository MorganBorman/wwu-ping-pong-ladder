from CASVerifiedRequestHandler import CASVerifiedRequestHandler
import json
import re

from sqlalchemy.sql.expression import desc, asc, label
import sqlalchemy.util._collections
from sqlalchemy import func, and_

from database.SessionFactory import SessionFactory

from database.User import User
from database.Match import Match
from database.Game import Game
from database.Score import Score
from database.Participation import Participation

import constants

from resultdict import resultdict
    
def get_match_history_query(session):

    #(game_id, score)

    winning_scores = session.query( Score.game_id, func.max(Score.score).label("score") ).\
                                group_by( Score.game_id ).subquery()
                            
    #(match_id, user_id, games_won)
                            
    game_winners = session.query(   Game.match_id,
                                    Score.user_id, 
                                    func.count(winning_scores.c.game_id).label("games_won") ).\
                              filter(   Game.id == Score.game_id ).\
                              filter(   winning_scores.c.game_id == Score.game_id ).\
                              filter(   Score.score == winning_scores.c.score ).\
                              group_by(Game.match_id, Score.user_id).subquery()

    #(match_id, user_id, games_won)
    
    match_game_counts = session.query( Participation.match_id,
                                       Participation.user_id,
                                       func.coalesce(game_winners.c.games_won, 0).label("games_won") ).\
                              outerjoin(game_winners, 
                                and_(game_winners.c.match_id == Participation.match_id, 
                                game_winners.c.user_id == Participation.user_id) ).subquery()
                                
    match_winners = session.query( match_game_counts.c.match_id, 
                                   match_game_counts.c.user_id, 
                                   User.displayname, 
                                   match_game_counts.c.games_won.label("games_won") ).\
                filter( match_game_counts.c.user_id == User.id ).\
                filter( match_game_counts.c.games_won >= 2 ).subquery()
                
    match_losers = session.query(  match_game_counts.c.match_id, 
                                   match_game_counts.c.user_id, 
                                   User.displayname, 
                                   match_game_counts.c.games_won.label("games_won") ).\
                filter( match_game_counts.c.user_id == User.id ).\
                filter( match_game_counts.c.games_won < 2 ).subquery()
                              
    match_history = session.query(  Match.id.label('id'),
                                    Match.date.label('date'),
                                    match_winners.c.games_won.label('winner_score'), 
                                    match_winners.c.user_id.label('winner_id'),
                                    match_winners.c.displayname.label('winner_displayname'),
                                    match_losers.c.games_won.label('opponent_score'),
                                    match_losers.c.user_id.label('opponent_id'),
                                    match_losers.c.displayname.label('opponent_displayname')).\
                        filter( match_winners.c.match_id == match_losers.c.match_id ).\
                        filter( Match.id == match_winners.c.match_id )
    
    return match_history

'''
session = SessionFactory()
try:
    print resultdict(get_match_history_query(session).all())
finally:
    session.close()
                    
quit()
'''

sorting_expression = re.compile(r"sort\((?P<direction>[\+|\-])(?P<column>\w+)\)")
range_expression = re.compile(r"items=(?P<lower>\d+)-(?P<upper>\d+)")

class MatchHistoryStore(CASVerifiedRequestHandler):
    def get(self, match_id):
        username = self.get_current_user()
        
        if username is None:
            self.validate_user()
            return
            
        user = User.get_user(username)
                
        if user.permission_level < constants.PERMISSION_LEVEL_USER:
            self.render("denied.html", user=user)
            return
        
        
        if match_id is not None and match_id != "":
            # single item
            user_id = int(match_id)
            
            session = SessionFactory()
            try:
                result = get_match_history_query(session).filter(Match.id == match_id).one()
                        
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
                    column = "date"
                    
            if column not in ["id", "date", "winner_id", "winner_score", "winner_displayname", "opponent_id", "opponent_score", "opponent_displayname"]:
                column = "date"

            if direction == '-':
                    direction = desc
            else:
                    direction = asc
            
            session = SessionFactory()
            try:
                query = get_match_history_query(session)
                        
                query = query.order_by(direction(column))
                        
                #query = query.slice(start, stop)
                        
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

