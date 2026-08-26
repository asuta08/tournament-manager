from typing import List

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from db.database import Base, engine, session_factory

from db.models import UserDB, TournamentDB, MatchDB
from tournament import Status, Match, Tournament


class Repository:

    @staticmethod
    def create_tables():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


class UserRepository:

    @staticmethod
    def insert_user(username):
        with session_factory() as session:
            new_user = UserDB(username=username)
            session.add(new_user)
            session.commit()
            return new_user.id


class TournamentRepository:

    @staticmethod
    def load_tournament(tournament_id):
        with session_factory() as session:
            tournament_db = session.get(TournamentDB, tournament_id)

            match_map = {}
            teams = set()

            for match_db in tournament_db.matches:
                teams.add(match_db.team1_id)
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

            tournament = Tournament(tournament_id=tournament_db.id, teams=list(teams))
            tournament.bracket = list(match_map.values())
            tournament.current_round = tournament_db.current_round
            tournament.status = tournament_db.status

            return tournament



    @staticmethod
    def insert_tournament(name, creator_id):
        with session_factory() as session:
            new_tournament = TournamentDB(name=name, creator_id=creator_id, status=Status.IN_PROGRESS)
            session.add(new_tournament)
            session.commit()
            return new_tournament.id

    @staticmethod
    def update_current_round(tournament_id):
        with session_factory() as session:
            tournament = session.get(TournamentDB, tournament_id)
            tournament.current_round += 1
            session.commit()

    @staticmethod
    def update_final(tournament_id, winner_id):
        with session_factory() as session:
            tournament = session.get(TournamentDB, tournament_id)
            tournament.winner_id = winner_id
            tournament.status = Status.FINISHED
            session.commit()

    @staticmethod
    def get_tournament_with_matches(tournament_id):
        with session_factory() as session:
            stmt = (
                select(TournamentDB)
                .where(TournamentDB.id == tournament_id)
                .options(selectinload(TournamentDB.matches))
            )
            result = session.scalars(stmt).first()
            return result

    @staticmethod
    def save_tournament(tournament):
        with session_factory() as session:
            tournament_db = session.get(TournamentDB, tournament.id)

            tournament_db.current_round = tournament.current_round
            tournament_db.status = tournament.status
            tournament_db.winner_id = tournament.winner_id

            for match in tournament.bracket:
                match_db = session.get(MatchDB, match.id)
                match_db.team1_id = match.team1_id
                match_db.team2_id = match.team2_id
                match_db.team1_score = match.team1_score
                match_db.team2_score = match.team2_score
                match_db.status = match.status
                match_db.winner_id = match.winner_id

            session.commit()

class MatchRepository:

    @staticmethod
    def insert_bracket(tournament_id, bracket: List[Match]):
        with session_factory() as session:

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
            session.flush()

            for match, match_db in compare.items():
                match.id = match_db.id
                if match.next_match is not None:
                    match_db.next_match_id = compare[match.next_match].id

            session.commit()

    @staticmethod
    def update_after_result(match_id, team1_score, team2_score, winner_id):
        with session_factory() as session:
            match = session.get(MatchDB, match_id)
            match.team1_score = team1_score
            match.team2_score = team2_score
            match.winner_id = winner_id
            match.status = Status.FINISHED

            if match.next_match_id is not None:
                next_match = session.get(MatchDB, match.next_match_id)
                if next_match.team1_id is None:
                    next_match.team1_id = winner_id
                elif next_match.team2_id is None:
                    next_match.team2_id = winner_id
            else:
                session.commit()
                return True

            session.commit()

        return False

    @staticmethod
    def get_match_by_id(match_id):
        with session_factory() as session:
            return session.get(MatchDB, match_id)

    @staticmethod
    def get_matches_by_round(tournament_id, round_):
        with session_factory() as session:
            stmt = (
                select(MatchDB)
                .where(and_(
                    MatchDB.tournament_id == tournament_id,
                    MatchDB.round == round_
                ))
            )
            result = session.scalars(stmt).all()
            return result
