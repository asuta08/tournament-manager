from enum import Enum
from random import shuffle
from typing import List
from exceptions import TournamentOperationError


class Status(Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Match:
    def __init__(self, round_: int, team1_id: int = None, team2_id: int = None, next_match: 'Match' = None):
        self.id = None
        self.team1_id = team1_id
        self.team2_id = team2_id
        self.round = round_
        self.status = Status.IN_PROGRESS
        self.next_match = next_match
        self.winner_id = None
        self.team1_score = None
        self.team2_score = None
        self.teams_count = 0

    def __repr__(self):
        if self.next_match is None:
            next_match_id = None
        else:
            next_match_id = self.next_match.id
        return (f'Match(id: {self.id}; Round: {self.round}; Team_1: {self.team1_id};'
                f' Team_2: {self.team2_id}; Status: {self.status}; Next_match_id: {next_match_id})')


class Tournament:

    def __init__(self, name: str, teams: List[int]):
        self.id = None
        self.name = name
        self.teams = teams
        self.bracket = None
        self.status = Status.IN_PROGRESS
        self.current_round = 1
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

    def _find_active_match(self, match_id: int) -> Match | None:
        for match in self.bracket:
            if match.id == match_id:
                if match.status != Status.IN_PROGRESS:
                    raise TournamentOperationError("Match is already finished!", 400)
                if match.round != self.current_round:
                    raise TournamentOperationError("Match is not in the current round!", 400)
                return match
        raise TournamentOperationError(f"Match with id: {match_id} not found!", 404)

    def _is_round_finished(self) -> bool:
        if all(m.status == Status.FINISHED for m in self.bracket if m.round == self.current_round):
            return True
        return False

    def handle_result(self, match_id: int, team1_score: int, team2_score: int) -> None:
        if self.status == Status.FINISHED:
            raise TournamentOperationError("Tournament is already finished!", 400)

        match = self._find_active_match(match_id)

        if match is None:
            raise TournamentOperationError(f"Match with id: {match_id} is not active!", 400)

        winner_id = match.team1_id if team1_score > team2_score else match.team2_id

        match.winner_id = winner_id
        match.team1_score = team1_score
        match.team2_score = team2_score
        match.status = Status.FINISHED

        if match.next_match is not None:
            if match.next_match.team1_id is None:
                match.next_match.team1_id = winner_id
            elif match.next_match.team2_id is None:
                match.next_match.team2_id = winner_id

        if self._is_round_finished():
            self.current_round += 1

        if match.next_match is None:
            self.status = Status.FINISHED
            self.winner_id = winner_id

    def __repr__(self):
        return f'Tournament(id: {self.id}; Current_round: {self.current_round}; Status: {self.status}; Winner: {self.winner_id})'
