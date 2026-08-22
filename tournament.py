from enum import Enum
from random import shuffle
from typing import List
from exceptions import MatchCreationError, TournamentCreationError, TournamentOperationError


class Status(Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Match:
    match_id = 1

    def __init__(self, round_: int, team1: str = None, team2: str = None, next_match: 'Match' = None):
        if team1 == team2 and team1 is not None:
            raise MatchCreationError("Teams must be different!")

        self._id = Match.match_id
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
            next_match_id = self.next_match._id
        return (f'Match(id: {self._id}; Round: {self.round}; Team_1: {self.team1};'
                f' Team_2: {self.team2}; Status: {self.status}; Next_Match_id: {next_match_id})')


class Tournament:
    tournament_id = 1

    def __init__(self, name: str, teams: List[str]):
        if len(teams) < 2:
            raise TournamentCreationError("The number of teams must be at least 2!")

        self._id = Tournament.tournament_id
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
        if self.status == Status.FINISHED:
            raise TournamentOperationError("Tournament is already finished!")

        if winner not in self.teams:
            raise TournamentOperationError(f"Team {winner} is not participating in this tournament!")

        match_found = False
        for match in self.bracket:
            if (match.team1 == winner or match.team2 == winner) \
                and match.team1 is not None and match.team2 is not None and match.status == Status.IN_PROGRESS:
                match_found = True
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

        if not match_found:
            raise TournamentOperationError(f"No active match found for team {winner}!")

    def determine_winner(self, match: Match, winner: str) -> None:
        match.status = Status.FINISHED
        self.status = Status.FINISHED
        self.winner = winner

    def __repr__(self):
        return f'Tournament(id: {self._id}; Name: {self.name}; Status: {self.status}; Winner: {self.winner})'
