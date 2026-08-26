import pytest

from exceptions import MatchCreationError, TournamentCreationError, TournamentOperationError
from tournament import Match, Status, Tournament


class TestMatch:

    def test_match_status(self):
        match = Match(1, 1, 2)
        assert match.status == Status.IN_PROGRESS

    def test_match_identical_teams(self):
        with pytest.raises(MatchCreationError):
            match = Match(1, 1, 1)


class TestTournament:

    @pytest.fixture
    def tournament(self):
        tournament = Tournament("test", [1, 2, 3, 4])
        tournament.create_bracket()
        return tournament

    def test_full_tournament_cycle_4_teams(self, tournament):
        match_id = tournament.bracket[0].id
        team1_id = tournament.bracket[0].team1_id
        tournament.handle_result(match_id, 1, 0)
        assert tournament.bracket[0].status == Status.FINISHED
        assert tournament.bracket[2].team1_id == team1_id

        match_id = tournament.bracket[1].id
        team1_id = tournament.bracket[1].team1_id
        tournament.handle_result(match_id, 1, 0)
        assert tournament.bracket[1].status == Status.FINISHED
        assert tournament.bracket[2].team2_id == team1_id
        assert tournament.current_round == 2

        match_id = tournament.bracket[2].id
        team1_id = tournament.bracket[2].team1_id
        tournament.handle_result(match_id, 1, 0)
        assert tournament.bracket[2].status == Status.FINISHED
        assert tournament.status == Status.FINISHED
        assert tournament.winner_id == team1_id

    def test_full_tournament_cycle_3_teams(self):
        tournament = Tournament("test", [1, 2, 3])
        tournament.create_bracket()

        assert tournament.bracket[1].team1_id is not None

        match_id = tournament.bracket[0].id
        team1_id = tournament.bracket[0].team1_id
        tournament.handle_result(match_id, 1, 0)
        assert tournament.bracket[0].status == Status.FINISHED
        assert tournament.bracket[1].team2_id == team1_id
        assert tournament.current_round == 2

        match_id = tournament.bracket[1].id
        team1_id = tournament.bracket[1].team1_id
        tournament.handle_result(match_id, 1, 0)
        assert tournament.bracket[1].status == Status.FINISHED
        assert tournament.status == Status.FINISHED
        assert tournament.winner_id == team1_id

    def test_next_match_correct(self, tournament):
        none_count = 0
        for match in tournament.bracket:
            assert match.teams_count == 2
            if match.next_match is None:
                none_count += 1
        assert none_count == 1

    @pytest.mark.parametrize(
        "teams, match_count",
        [
            ([1, 2], 1),
            ([1, 2, 3], 2),
            ([1, 2, 3, 4], 3),
            ([1, 2, 3, 4, 5], 4),
            ([1, 2, 3, 4, 5, 6], 5),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 12),
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
            [1],
        ]
    )
    def test_not_enough_teams(self, teams):
        with pytest.raises(TournamentCreationError):
            tournament = Tournament("test", teams)

    def test_handle_result_twice(self, tournament):
        match_id = tournament.bracket[0].id
        tournament.handle_result(match_id, 1, 0)
        assert tournament.bracket[0].status == Status.FINISHED
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(match_id, 1, 0)

    def test_handle_result_finished_tournament(self):
        tournament = Tournament("test", [1, 2, 3])
        tournament.create_bracket()
        match_id = tournament.bracket[0].id
        tournament.handle_result(match_id, 1, 0)
        match_id = tournament.bracket[1].id
        tournament.handle_result(match_id, 1, 0)
        assert tournament.status == Status.FINISHED
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(match_id, 1, 0)

    def test_handle_result_nonexistent_match(self, tournament):
        match_id = 42
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(match_id, 1, 0)

    def test_handle_results_out_of_order(self, tournament):
        match_id = tournament.bracket[1].id
        tournament.handle_result(match_id, 1, 0)

        match_id = tournament.bracket[0].id
        tournament.handle_result(match_id, 1, 0)

        final = tournament.bracket[2]
        assert final.team1_id is not None
        assert final.team2_id is not None
