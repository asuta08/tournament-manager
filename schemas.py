from typing import List
from pydantic import BaseModel, Field, field_validator


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=30)


class TournamentSchema(BaseModel):
    user_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    teams: List[int] = Field(min_length=2, max_length=64)

    @field_validator('teams')
    @classmethod
    def unique_teams(cls, v: List[int]) -> List[int]:
        if len(v) != len(set(v)):
            raise ValueError("Teams must be unique!")
        return v


class MatchResultSchema(BaseModel):
    team1_score: int = Field(ge=0)
    team2_score: int = Field(ge=0)