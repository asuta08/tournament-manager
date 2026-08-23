from enum import Enum
from random import shuffle
from typing import List
from exceptions import MatchCreationError, TournamentCreationError, TournamentOperationError


class Status(Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Match:
    def __init__(self, round_: int, team1_id: int  = None, team2_id: int  = None, next_match: 'Match' = None):
        if team1_id == team2_id and team1_id is not None:
            raise MatchCreationError("Teams must be different!")

        self.id = None
        self.team1_id = team1_id
        self.team2_id = team2_id
        self.round = round_
        self.status = Status.IN_PROGRESS
        self.next_match = next_match
        self.winner_id = None
        self.teams_count = 0

    def __repr__(self):
        if self.next_match is None:
            next_match_id = None
        else:
            next_match_id = self.next_match.id
        return (f'Match(id: {self.id}; Round: {self.round}; Team_1: {self.team1_id};'
                f' Team_2: {self.team2_id}; Status: {self.status}; Next_match_id: {next_match_id})')


class Tournament:
    tournament_id = 1

    def __init__(self, name: str, teams: List[int]):
        if len(teams) < 2:
            raise TournamentCreationError("The number of teams must be at least 2!")

        self._id = Tournament.tournament_id
        Tournament.tournament_id += 1
        self.name = name
        self.teams = teams
        self.bracket = None
        self.status = Status.IN_PROGRESS
        self.winner_id = None

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
                        match.team1_id = extra_team
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

    def handle_result(self, winner_id: int) -> None:
        if self.status == Status.FINISHED:
            raise TournamentOperationError("Tournament is already finished!")

        if winner_id not in self.teams:
            raise TournamentOperationError(f"Team {winner_id} is not participating in this tournament!")

        match_found = False
        for match in self.bracket:
            if (match.team1_id == winner_id or match.team2_id == winner_id) \
                and match.team1_id is not None and match.team2_id is not None and match.status == Status.IN_PROGRESS:
                match_found = True
                if match.next_match is None:
                    self.determine_winner(match, winner_id)
                    break
                if match.next_match.team1_id is None:
                    match.next_match.team1_id = winner_id
                    match.status = Status.FINISHED
                    break
                if match.next_match.team2_id is None:
                    match.next_match.team2_id = winner_id
                    match.status = Status.FINISHED
                    break

        if not match_found:
            raise TournamentOperationError(f"No active match found for team with id: {winner_id}!")

    def determine_winner(self, match: Match, winner_id: int) -> None:
        match.status = Status.FINISHED
        self.status = Status.FINISHED
        self.winner_id = winner_id

    def __repr__(self):
        return f'Tournament(id: {self._id}; Name: {self.name}; Status: {self.status}; Winner: {self.winner_id})'
