from enum import Enum
from random import shuffle
from typing import List, Self

class Status(Enum):
    IN_PROGRESS = "in_progress",
    FINISHED = "finished"

class Match:
    match_id = 1
    def __init__(self, team1: str = None, team2: str = None, next_match: Self = None):
        self.id = Match.match_id
        Match.match_id += 1
        self.team1 = team1
        self.team2 = team2
        self.next_match = next_match
        self.status = Status.IN_PROGRESS
    def __repr__(self):
        if self.next_match is None:
            next_match_id = None
        else:
            next_match_id = self.next_match.id
        return f'Match(id: {self.id}; Team_1: {self.team1}; Team_2: {self.team2}; Status: {self.status}; Next_Match_id: {next_match_id})'


def create_bracket(teams: List[str]) -> List[Match]:
    shuffle(teams)
    matches_count = len(teams) - 1
    bracket = []

    while teams:
        team1 = teams.pop()
        team2 = teams.pop()
        match = Match(team1, team2)
        bracket.append(match)

    match_pos = 0
    for _ in range(matches_count - len(bracket)):
        future_match = Match()
        bracket[match_pos].next_match = future_match
        bracket[match_pos + 1].next_match = future_match
        match_pos += 2
        bracket.append(future_match)

    return bracket

def handle_result(bracket: List[Match], winner: str):
    for match in bracket:
        if match.team1 == winner or match.team2 == winner and match.status == Status.IN_PROGRESS:
            if match.next_match.team1 is None:
                match.next_match.team1 = winner
                match.status = Status.FINISHED
                break
            if match.next_match.team2 is None:
                match.next_match.team2 = winner
                match.status = Status.FINISHED
                break




teams1 = ["A", "B", "C", "D"]
bracket1 = create_bracket(teams1)
print(bracket1)
handle_result(bracket1, bracket1[0].team1)
print(bracket1)
handle_result(bracket1, bracket1[1].team2)
print(bracket1)
