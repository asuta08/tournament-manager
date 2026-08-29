from typing import List, Dict, Any

from db.repository import TournamentRepository, MatchRepository, UserRepository
from exceptions import TournamentRepositoryError
from tournament import Tournament


class Service:
    @staticmethod
    def create_user(username: str) -> int:
        user_id = UserRepository.insert_user(username)
        return user_id

    @staticmethod
    def get_user(user_id: int) -> Dict[str, Any]:
        user = UserRepository.get_user(user_id)

        if user is None:
            raise TournamentRepositoryError("User not found!", 404)

        return {"user_id": user_id, "username": user.username}

    @staticmethod
    def create_tournament(user_id: int, name: str, teams: List[int]) -> int:
        tournament = Tournament(name, teams)
        tournament.create_bracket()

        tournament_id = TournamentRepository.insert_tournament(name, user_id)
        tournament.id = tournament_id
        MatchRepository.insert_bracket(tournament_id, tournament.bracket)

        return tournament_id

    @staticmethod
    def get_tournament(tournament_id: int) -> Dict[str, Any]:
        tournament = TournamentRepository.load_tournament(tournament_id)

        if tournament is None:
            raise TournamentRepositoryError("Tournament not found!", 404)

        return {
            "tournament_id": tournament.id,
            "name": tournament.name,
            "current_round": tournament.current_round,
            "status": tournament.status,
            "winner_id": tournament.winner_id
        }

    @staticmethod
    def handle_match_result(match_id: int, team1_score: int, team2_score: int) -> None:
        match_db = MatchRepository.get_match_by_id(match_id)

        if match_db is None:
            raise TournamentRepositoryError("Match not found!", 404)

        tournament = TournamentRepository.load_tournament(match_db.tournament_id)

        tournament.handle_result(match_id, team1_score, team2_score)

        TournamentRepository.save_tournament(tournament)

    @staticmethod
    def get_bracket(tournament_id: int) -> Dict[str, List[Dict[str, Any]]]:
        tournament = TournamentRepository.load_tournament(tournament_id)

        if tournament is None:
            raise TournamentRepositoryError("Tournament not found!", 404)

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

    @staticmethod
    def get_match(match_id: int) -> Dict[str, Any]:
        match_db = MatchRepository.get_match_by_id(match_id)

        if match_db is None:
            raise TournamentRepositoryError("Match not found!", 404)

        return {
            "match_id": match_id,
            "team1_id": match_db.team1_id,
            "team2_id": match_db.team2_id,
            "team1_score": match_db.team1_score,
            "team2_score": match_db.team2_score,
            "status": match_db.status,
            "winner_id": match_db.winner_id
        }