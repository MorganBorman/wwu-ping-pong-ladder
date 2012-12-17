import sqlalchemy.util._collections
from sqlalchemy import func

from database.SessionFactory import SessionFactory

from database.User import User
from database.Match import Match
from database.Game import Game
from database.Score import Score
from database.Participation import Participation
from database.TrueSkillCache import TrueSkillCache
        
import trueskill
import time

from resultdict import resultdict

trueskill.setup()

def get_most_recent_ratings(user_id):
    from sqlalchemy.orm.exc import NoResultFound
    session = SessionFactory()
    try:
        participation_matches = session.query( Match.id.label("match_id"), 
                                               Match.date_recorded.label("date") ).\
                                filter( Participation.user_id == user_id ).\
                                filter( Participation.match_id == Match.id ).subquery()
                                
        most_recent_match_date = session.query( participation_matches.c.match_id.label("match_id"),
                                                func.max(participation_matches.c.date).label("date") ).\
                                subquery()
                                
        most_recent_match = session.query( participation_matches.c.match_id.label("match_id") ).\
                                filter( participation_matches.c.date == most_recent_match_date.c.date ).\
                                subquery()
                                
        most_recent_ratings = session.query( TrueSkillCache.sigma.label("sigma"),
                                             TrueSkillCache.mu.label("mu") ).\
                                filter( TrueSkillCache.user_id == user_id ).\
                                filter( most_recent_match.c.match_id == TrueSkillCache.match_id ).one()
        
        return resultdict(most_recent_ratings)
    except NoResultFound:
        return {'mu': trueskill.MU, 'sigma': trueskill.SIGMA}
    finally:
        session.close()

def create_match(session, user1, user2, timestamp, games):
    """Creates and adds a match to the session given two users a unix timestamp and a list of score pairs."""
    match = Match(timestamp, int(time.time()))
    
    p1 = Participation()
    user1.participations.append(p1)
    match.participations.append(p1)
    
    p2 = Participation()
    user2.participations.append(p2)
    match.participations.append(p2)
    
    p1_wins = len(filter(lambda g: g[0] > g[1], games))
    p2_wins = len(filter(lambda g: g[0] < g[1], games))
    
    u1ratings = get_most_recent_ratings(user1.id)
    u2ratings = get_most_recent_ratings(user2.id)
    
    p1rating = trueskill.Rating(**u1ratings)
    p2rating = trueskill.Rating(**u2ratings)
    
    if p1_wins > p2_wins:
        ranks = [0, 1]
    else:
        ranks = [1, 0]
    
    new_ratings = trueskill.transform_ratings([(p1rating,), (p2rating,)], ranks=ranks)
    (p1rating,), (p2rating,) = new_ratings
    
    true_skill_rating1 = TrueSkillCache(p1rating.sigma, p1rating.mu, p1rating.exposure)
    match.true_skill_ratings.append(true_skill_rating1)
    user1.true_skill_ratings.append(true_skill_rating1)
    
    true_skill_rating2 = TrueSkillCache(p2rating.sigma, p2rating.mu, p2rating.exposure)
    match.true_skill_ratings.append(true_skill_rating2)
    user2.true_skill_ratings.append(true_skill_rating2)
    
    for game_scores in games:
        game = Game(match)
        
        s1 = Score(game_scores[0])
        game.scores.append(s1)
        user1.scores.append(s1)
        
        s2 = Score(game_scores[1])
        game.scores.append(s2)
        user2.scores.append(s2)
        
        match.games.append(game)
        
    session.add(match)
