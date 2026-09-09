from typing import List, Dict, Any

from app.db.repository import TournamentRepository, MatchRepository, UserRepository
from app.core.exceptions import TournamentRepositoryError
from app.core.tournament import Tournament


class Service:
    @staticmethod
    async def create_user(username: str, hashed_password: str) -> int:
        user_id = await UserRepository.insert_user(username, hashed_password)
        return user_id

    @staticmethod
    async def get_user(user_id: int) -> Dict[str, Any]:
        user = await UserRepository.get_user_by_id(user_id)
        return {"user_id": user_id, "username": user.username}

    @staticmethod
    async def get_user_by_username(username: str) -> Dict[str, Any] | None:
        user = await UserRepository.get_user_by_username(username)
        if user is None:
            return None
        return {"user_id": user.id, "hashed_password": user.hashed_password}

    @staticmethod
    async def create_tournament(user_id: int, name: str, teams: List[int]) -> int:
        tournament = Tournament(name, teams)
        tournament.create_bracket()

        tournament_id = await TournamentRepository.insert_tournament(name, user_id)
        tournament.id = tournament_id
        await MatchRepository.insert_bracket(tournament_id, tournament.bracket)

        return tournament_id

    @staticmethod
    async def get_tournament(tournament_id: int) -> Dict[str, Any]:
        tournament = await TournamentRepository.load_tournament(tournament_id)

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
    async def handle_match_result(match_id: int, team1_score: int, team2_score: int) -> None:
        match_db = await MatchRepository.get_match_by_id(match_id)

        if match_db is None:
            raise TournamentRepositoryError("Match not found!", 404)

        tournament = await TournamentRepository.load_tournament(match_db.tournament_id)

        tournament.handle_result(match_id, team1_score, team2_score)

        await TournamentRepository.save_tournament(tournament)

    @staticmethod
    async def get_bracket(tournament_id: int) -> Dict[str, List[Dict[str, Any]]]:
        tournament = await TournamentRepository.load_tournament(tournament_id)

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
    async def get_match(match_id: int) -> Dict[str, Any]:
        match_db = await MatchRepository.get_match_by_id(match_id)

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