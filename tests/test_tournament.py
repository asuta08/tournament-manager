import pytest

from exceptions import MatchCreationError, TournamentCreationError, TournamentOperationError
from tournament import Match, Status, Tournament


class TestMatch:

    def test_match_id(self):
        Match.match_id = 1
        m1 = Match(1, "A", "B")
        m2 = Match(1, "C", "D")
        assert m1.id == 1
        assert m2.id == 2

    def test_match_status(self):
        match = Match(1, "A", "B")
        assert match.status == Status.IN_PROGRESS

    def test_match_identical_teams(self):
        with pytest.raises(MatchCreationError):
            match = Match(1, "A", "A")


class TestTournament:

    @pytest.mark.parametrize(
        "teams, match_count",
        [
            (["A", "B"], 1),
            (["A", "B", "C"], 2),
            (["A", "B", "C", "D"], 3),
            (["A", "B", "C", "D", "E"], 4),
            (["A", "B", "C", "D", "E", "F"], 5),
            (["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"], 12),
        ]
    )
    def test_bracket_size(self, teams, match_count):
        tournament = Tournament("test", teams)
        tournament.create_bracket()
        assert len(tournament.bracket) == match_count

    @pytest.mark.parametrize(
        "teams",
        [
            [],
            ["A"],
        ]
    )
    def test_not_enough_teams(self, teams):
        with pytest.raises(TournamentCreationError):
            tournament = Tournament("test", teams)

    def test_handle_result_twice(self):
        tournament = Tournament("test", ["A", "B", "C", "D"])
        tournament.create_bracket()
        team = tournament.bracket[0].team1
        tournament.handle_result(team)
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(team)

    def test_handle_result_finished_tournament(self):
        tournament = Tournament("test", ["A", "B", "C"])
        tournament.create_bracket()
        team = tournament.bracket[0].team1
        tournament.handle_result(team)
        team = tournament.bracket[1].team1
        tournament.handle_result(team)
        assert tournament.status == Status.FINISHED
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(team)

    def test_handle_result_outside_team(self):
        tournament = Tournament("test", ["A", "B", "C"])
        tournament.create_bracket()
        team = "Z"
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(team)