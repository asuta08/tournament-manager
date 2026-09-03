from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator


class UserAuthSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=30)


class TournamentSchema(BaseModel):
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

    @model_validator(mode='after')
    def check_no_draw(self) -> 'MatchResultSchema':
        if self.team1_score == self.team2_score:
            raise ValueError("Draws are not allowed!")
        return self