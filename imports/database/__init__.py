from engine import engine

import User
import Match
import Participation
import Game
import Score
import TrueSkillCache

from Base import Base

Base.metadata.create_all(engine)
