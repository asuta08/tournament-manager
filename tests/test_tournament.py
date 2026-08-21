import pytest

from exceptions import MatchCreationError, TournamentCreationError
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

