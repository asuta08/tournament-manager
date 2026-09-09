from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import async_session_factory

from app.db.models import UserDB, TournamentDB, MatchDB
from app.core.tournament import Status, Match, Tournament


class UserRepository:

    @staticmethod
    async def insert_user(username: str, hashed_password: str) -> int:
        async with async_session_factory() as session:
            new_user = UserDB(username=username, hashed_password=hashed_password)
            session.add(new_user)
            await session.flush()
            user_id = new_user.id
            await session.commit()
            return user_id

    @staticmethod
    async def get_user_by_id(user_id: int) -> UserDB:
        async with async_session_factory() as session:
            stmt = (
                select(UserDB)
                .where(UserDB.id == user_id)
            )
            result = await session.execute(stmt)
            user = result.scalar()
            return user

    @staticmethod
    async def get_user_by_username(username: str) -> UserDB:
        async with async_session_factory() as session:
            stmt = (
                select(UserDB).
                where(UserDB.username == username)
            )
            result = await session.execute(stmt)
            user = result.scalar()
            return user


class TournamentRepository:

    @staticmethod
    async def load_tournament(tournament_id: int) -> Tournament | None:
        async with async_session_factory() as session:
            stmt = (
                select(TournamentDB)
                .where(TournamentDB.id == tournament_id)
                .options(selectinload(TournamentDB.matches))
            )

            result = await session.execute(stmt)
            tournament_db = result.scalar()

            if tournament_db is None:
                return None

            match_map = {}
            teams = set()

            for match_db in tournament_db.matches:
                if match_db.team1_id is not None:
                    teams.add(match_db.team1_id)
                if match_db.team2_id is not None:
                    teams.add(match_db.team2_id)
                match = Match(match_db.round, match_db.team1_id, match_db.team2_id)
                match.id = match_db.id
                match.team1_score = match_db.team1_score
                match.team2_score = match_db.team2_score
                match.winner_id = match_db.winner_id
                match.status = match_db.status
                match_map[match_db.id] = match

            for match_db in tournament_db.matches:
                match = match_map[match_db.id]
                if match_db.next_match_id is not None:
                    match.next_match = match_map[match_db.next_match_id]

            tournament = Tournament(name=tournament_db.name, teams=list(teams))
            tournament.id = tournament_db.id
            tournament.bracket = list(match_map.values())
            tournament.current_round = tournament_db.current_round
            tournament.status = tournament_db.status
            tournament.winner_id = tournament_db.winner_id

            return tournament

    @staticmethod
    async def insert_tournament(name: str, creator_id: int) -> int:
        async with async_session_factory() as session:
            new_tournament = TournamentDB(name=name, creator_id=creator_id, status=Status.IN_PROGRESS)
            session.add(new_tournament)
            await session.flush()
            tournament_id = new_tournament.id
            await session.commit()
            return tournament_id

    @staticmethod
    async def save_tournament(tournament: Tournament) -> None:
        async with async_session_factory() as session:
            stmt = (
                select(TournamentDB)
                .where(TournamentDB.id == tournament.id)
                .options(selectinload(TournamentDB.matches))
            )

            result = await session.execute(stmt)
            tournament_db = result.scalar()

            tournament_db.name = tournament.name
            tournament_db.current_round = tournament.current_round
            tournament_db.status = tournament.status
            tournament_db.winner_id = tournament.winner_id

            match_ids = [match.id for match in tournament.bracket]
            match_stmt = (
                select(MatchDB)
                .where(MatchDB.id.in_(match_ids))
            )
            matches_res = await session.execute(match_stmt)
            matches_db = matches_res.scalars().all()
            match_map = {match.id: match for match in matches_db}

            for match in tournament.bracket:
                match_db = match_map[match.id]
                match_db.team1_id = match.team1_id
                match_db.team2_id = match.team2_id
                match_db.team1_score = match.team1_score
                match_db.team2_score = match.team2_score
                match_db.status = match.status
                match_db.winner_id = match.winner_id

            await session.commit()

class MatchRepository:

    @staticmethod
    async def insert_bracket(tournament_id: int, bracket: List[Match]) -> None:
        async with async_session_factory() as session:

            compare = {}
            new_matches = []
            for match in bracket:
                new_match = MatchDB(
                    tournament_id=tournament_id,
                    round=match.round,
                    team1_id=match.team1_id,
                    team2_id=match.team2_id,
                    status=Status.IN_PROGRESS
                )
                compare[match] = new_match
                new_matches.append(new_match)
            session.add_all(new_matches)
            await session.flush()

            for match, match_db in compare.items():
                match.id = match_db.id
                if match.next_match is not None:
                    match_db.next_match_id = compare[match.next_match].id

            await session.commit()

    @staticmethod
    async def get_match_by_id(match_id: int) -> MatchDB:
        async with async_session_factory() as session:
            stmt = (
                select(MatchDB)
                .where(MatchDB.id == match_id)
            )
            result = await session.execute(stmt)
            match = result.scalar()
            return match