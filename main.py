from db.repository import Repository, UserRepository, TournamentRepository
from service import Service


Repository.create_tables()

user_id = UserRepository.insert_user("Dexter Morgan")

tournament_id = Service.create_tournament(user_id, "test", [1, 2, 3, 4])



Service.handle_match_result(1, 3, 2)
Service.handle_match_result(2, 0, 1)
Service.handle_match_result(3, 2, 1)


# test_tournament = Tournament("test", [1, 2, 3, 4, 5, 6, 7, 8])
# test_tournament.create_bracket()
# MatchRepository.insert_bracket(tour_id, test_tournament.bracket)

# tour2_id = TournamentRepository.insert_tournament("test2", user_id)
# test_tournament2 = Tournament("test2", [1, 2, 3, 4, 5])
# test_tournament2.create_bracket()
# MatchRepository.insert_bracket(tour2_id, test_tournament2.bracket)


# team_id = test_tournament.bracket[0].team1_id
# m_id = test_tournament.handle_result(team_id)
# MatchRepository.update_after_result(m_id, 3, 2, team_id)
# team_id = test_tournament.bracket[1].team1_id
# m_id = test_tournament.handle_result(team_id)
# MatchRepository.update_after_result(m_id, 3, 2, team_id)
# TournamentRepository.update_current_round(1)
# m_id = test_tournament.handle_result(team_id)
# MatchRepository.update_after_result(m_id, 3, 2, team_id)