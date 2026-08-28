from typing import List
from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str

class TournamentSchema(BaseModel):
    user_id: int
    name: str
    teams: List[int]

class MatchResultSchema(BaseModel):
    team1_score: int
    team2_score: int