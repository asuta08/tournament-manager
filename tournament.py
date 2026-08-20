from enum import Enum
from random import shuffle
from typing import List, Self


class Status(Enum):
    IN_PROGRESS = "in_progress"
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


class Tournament:
    tournament_id = 1

    def __init__(self, name: str, teams: List[str]):
        self.id = Tournament.tournament_id
        Tournament.tournament_id += 1
        self.name = name
        self.teams = teams
        self.bracket = None
        self.status = Status.IN_PROGRESS
        self.winner = None

    def create_bracket(self) -> List[Match]:
        teams = self.teams.copy()

        if len(teams) < 2:
            return []

        shuffle(teams)
        teams_count = len(teams)
        bracket = []
        extra_team = None

        curr_round = 1
        while teams_count > 1:
            matches_in_round = teams_count // 2
            bye_teams = teams_count % 2

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

        self.bracket = bracket
        return bracket

    def handle_result(self, winner: str) -> None:
        for match in self.bracket:
            if (match.team1 == winner or match.team2 == winner) and match.status == Status.IN_PROGRESS:
                if match.next_match is None:
                    self.determine_winner(match, winner)
                    break
                if match.next_match.team1 is None:
                    match.next_match.team1 = winner
                    match.status = Status.FINISHED
                    break
                if match.next_match.team2 is None:
                    match.next_match.team2 = winner
                    match.status = Status.FINISHED
                    break

    def determine_winner(self, match: Match, winner: str) -> None:
        match.status = Status.FINISHED
        self.status = Status.FINISHED
        self.winner = winner

    def __repr__(self):
        return f'Tournament(id: {self.id}; Name: {self.name}; Status: {self.status}; Winner: {self.winner})'


def print_bracket(bracket):
    for x in bracket:
        print(x)
    print()


teams1 = ["A", "B", "C", "D"]
tournament = Tournament("Test Championship", teams1)
tournament.create_bracket()
print(tournament)
bracket1 = tournament.bracket
print_bracket(bracket1)
tournament.handle_result(bracket1[0].team1)
print_bracket(bracket1)
tournament.handle_result(bracket1[1].team1)
print_bracket(bracket1)
tournament.handle_result(bracket1[2].team1)
print_bracket(bracket1)
print(tournament.winner)
print(tournament)