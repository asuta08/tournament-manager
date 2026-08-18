import math
from enum import Enum
from random import shuffle
from typing import List, Self

class Status(Enum):
    IN_PROGRESS = "in_progress",
    FINISHED = "finished"

class Match:
    match_id = 1

    def __init__(self, round_: int, team1: str = None, team2: str = None, next_match: Self = None):
        self.id = Match.match_id
        Match.match_id += 1
        self.team1 = team1
        self.team2 = team2
        self.round = round_
        self.status = Status.IN_PROGRESS
        self.next_match = next_match

    def __repr__(self):
        if self.next_match is None:
            next_match_id = None
        else:
            next_match_id = self.next_match.id
        return f'Match(id: {self.id}; Round: {self.round}; Team_1: {self.team1}; Team_2: {self.team2}; Status: {self.status}; Next_Match_id: {next_match_id})'


def create_bracket(teams: List[str]) -> List[Match]:
    if len(teams) < 2:
        return []

    shuffle(teams)
    teams_count = len(teams)
    bracket = []
    rounds = []

    curr_round = 1
    while teams_count > 1:
        matches_in_round = math.ceil(teams_count / 2)
        round_array = []
        for _ in range(matches_in_round):
            if len(teams) > 0:
                team1 = teams.pop()
                team2 = teams.pop()
                match = Match(curr_round, team1, team2)
            else:
                match = Match(curr_round)
            bracket.append(match)
            round_array.append(match)
        rounds.append(round_array)
        teams_count = matches_in_round
        curr_round += 1

    curr_round = 0
    for _ in range(len(rounds) - 1):
        match_pos = 0
        for match in rounds[curr_round]:
            match.next_match = rounds[curr_round + 1][match_pos // 2]
            match_pos += 1
        curr_round += 1

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




teams1 = ["A", "B", "C", "D", "E", "F", "G", "H"]
bracket1 = create_bracket(teams1)
for x in bracket1:
    print(x)
# handle_result(bracket1, bracket1[0].team1)
# print(bracket1)
# handle_result(bracket1, bracket1[1].team2)
# print(bracket1)
