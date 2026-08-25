from db.repository import TournamentRepository, MatchRepository
from tournament import Tournament, Status


class Service:

    @staticmethod
    def create_tournament(user_id, name, teams):

        tournament = Tournament(name, teams)
        tournament.create_bracket()

        tournament_id = TournamentRepository.insert_tournament(name, user_id)
        MatchRepository.insert_bracket(tournament_id, tournament.bracket)

        return tournament_id

    @staticmethod
    def handle_match_result(match_id, team1_score, team2_score):

        match = MatchRepository.get_match_by_id(match_id)

        if team1_score > team2_score:
            winner_id = match.team1_id
        else:
            winner_id = match.team2_id

        final = MatchRepository.update_after_result(match_id, team1_score, team2_score, winner_id)
        if final:
            TournamentRepository.update_final(match.tournament_id, winner_id)
            return winner_id

        matches = MatchRepository.get_matches_by_round(match.tournament_id, match.round)

        if all(m.status == Status.FINISHED for m in matches):
            TournamentRepository.update_current_round(match.tournament_id)

    @staticmethod
    def get_bracket(tournament_id):

        tournament = TournamentRepository.get_tournament_with_matches(tournament_id)

        bracket = {"rounds": []}
        temp_dict = {"round": 1, "matches": []}
        for match in sorted(tournament.matches, key= lambda m: m.round):
            if match.round == temp_dict["round"]:
                temp_dict["matches"].append({
                    "match_id": match.id,
                    "team1_id": match.team1_id,
                    "team2_id": match.team2_id,
                    "status": match.status
                })
            else:
                bracket["rounds"].append(temp_dict)
                temp_dict = {
                    "round": match.round,
                    "matches": [{
                        "match_id": match.id,
                        "team1_id": match.team1_id,
                        "team2_id": match.team2_id,
                        "status": match.status
                    }]
                }
        bracket["rounds"].append(temp_dict)

        return bracket