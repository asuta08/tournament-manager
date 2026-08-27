from typing import List, Dict, Any

from db.repository import TournamentRepository, MatchRepository
from tournament import Tournament


class Service:

    @staticmethod
    def create_tournament(user_id: int, name: str, teams: List[int]) -> int:

        tournament = Tournament(name, teams)
        tournament.create_bracket()

        tournament_id = TournamentRepository.insert_tournament(name, user_id)
        tournament.id = tournament_id
        MatchRepository.insert_bracket(tournament_id, tournament.bracket)

        return tournament_id

    @staticmethod
    def handle_match_result(match_id: int, team1_score: int, team2_score: int) -> None:

        match_db = MatchRepository.get_match_by_id(match_id)
        tournament = TournamentRepository.load_tournament(match_db.tournament_id)

        tournament.handle_result(match_id, team1_score, team2_score)

        TournamentRepository.save_tournament(tournament)

    @staticmethod
    def get_bracket(tournament_id: int) -> Dict[str, List[Dict[str, Any]]]:

        tournament = TournamentRepository.load_tournament(tournament_id)

        bracket = {"rounds": []}
        temp_dict = {"round": 1, "matches": []}
        for match in sorted(tournament.bracket, key= lambda m: m.round):
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