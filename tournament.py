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

        self.teams_count = 0

    def __repr__(self):
        if self.next_match is None:
            next_match_id = None
        else:
            next_match_id = self.next_match.id
        return (f'Match(id: {self.id}; Round: {self.round}; Team_1: {self.team1};'
                f' Team_2: {self.team2}; Status: {self.status}; Next_Match_id: {next_match_id}; Teams_count: {self.teams_count})')


def bye(bye_match: Match):
    bye_match.next_match.team2 = bye_match.team1


def create_bracket(teams: List[str]) -> List[Match]:
    if len(teams) < 2:
        return []

    shuffle(teams)
    teams_count = len(teams)
    bracket = []
    rounds = []
    bye_rounds = []
    extra_team = None

    curr_round = 1
    while teams_count > 1:
        matches_in_round = teams_count // 2
        bye_teams = teams_count % 2
        bye_rounds.append(bye_teams)
        round_array = []

        if bye_teams:
            if len(teams) > 1:
                extra_team = teams.pop()

        for _ in range(matches_in_round):
            if len(teams) > 1:
                team1 = teams.pop()
                team2 = teams.pop()
                match = Match(curr_round, team1, team2)
                match.teams_count = 2
            else:
                match = Match(curr_round)
                if extra_team is not None:
                    match.team1 = extra_team
                    match.teams_count = 1
                    extra_team = None
            bracket.append(match)
            round_array.append(match)

        rounds.append(round_array)
        teams_count = matches_in_round + bye_teams
        curr_round += 1

    slot_pointer = 0
    for match in bracket:
        while slot_pointer < len(bracket) and (
                bracket[slot_pointer].round <= match.round or bracket[slot_pointer].teams_count >= 2
        ):
            slot_pointer += 1
        if slot_pointer < len(bracket):
            match.next_match = bracket[slot_pointer]
            bracket[slot_pointer].teams_count += 1

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

def print_bracket(bracket):
    for x in bracket:
        print(x)
    print()


teams1 = ["A", "B", "C", "D", "E", "F"]
bracket1 = create_bracket(teams1)
print_bracket(bracket1)
# handle_result(bracket1, bracket1[0].team1)
# print_bracket(bracket1)
# handle_result(bracket1, bracket1[1].team2)
# print_bracket(bracket1)
