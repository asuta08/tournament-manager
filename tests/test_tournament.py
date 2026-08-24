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
        team = tournament.bracket[0].team1_id
        tournament.handle_result(team)
        assert tournament.bracket[0].status == Status.FINISHED
        assert tournament.bracket[2].team1_id == team

        team = tournament.bracket[1].team1_id
        tournament.handle_result(team)
        assert tournament.bracket[1].status == Status.FINISHED
        assert tournament.bracket[2].team2_id == team
        assert tournament.current_round == 2

        team = tournament.bracket[2].team1_id
        tournament.handle_result(team)
        assert tournament.bracket[2].status == Status.FINISHED
        assert tournament.status == Status.FINISHED
        assert tournament.winner_id == team

    def test_full_tournament_cycle_3_teams(self):
        tournament = Tournament("test", [1, 2, 3])
        tournament.create_bracket()

        assert tournament.bracket[1].team1_id is not None

        team = tournament.bracket[0].team1_id
        tournament.handle_result(team)
        assert tournament.bracket[0].status == Status.FINISHED
        assert tournament.bracket[1].team2_id == team
        assert tournament.current_round == 2

        team = tournament.bracket[1].team1_id
        tournament.handle_result(team)
        assert tournament.bracket[1].status == Status.FINISHED
        assert tournament.status == Status.FINISHED
        assert tournament.winner_id == team

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
        team = tournament.bracket[0].team1_id
        tournament.handle_result(team)
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(team)

    def test_handle_result_finished_tournament(self):
        tournament = Tournament("test", [1, 2, 3])
        tournament.create_bracket()
        team = tournament.bracket[0].team1_id
        tournament.handle_result(team)
        team = tournament.bracket[1].team1_id
        tournament.handle_result(team)
        assert tournament.status == Status.FINISHED
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(team)

    def test_handle_result_outside_team(self, tournament):
        team = 42
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(team)

    def test_handle_result_loser(self, tournament):
        team1 = tournament.bracket[0].team1_id
        tournament.handle_result(team1)
        team2 = tournament.bracket[0].team2_id
        with pytest.raises(TournamentOperationError):
            tournament.handle_result(team2)

    def test_handle_results_out_of_order(self, tournament):
        team = tournament.bracket[1].team1_id
        tournament.handle_result(team)

        team = tournament.bracket[0].team1_id
        tournament.handle_result(team)

        final = tournament.bracket[2]
        assert final.team1_id is not None
        assert final.team2_id is not None
