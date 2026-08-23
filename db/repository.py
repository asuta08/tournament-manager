from db.database import Base, engine, session_factory

from models import UserDB, TournamentDB, MatchDB
from tournament import Status


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
    def insert_tournament(name, creator_id):
        with session_factory() as session:
            new_tournament = TournamentDB(name=name, creator_id=creator_id, status=Status.IN_PROGRESS)
            session.add(new_tournament)
            session.commit()
            return new_tournament.id


class MatchRepository:

    @staticmethod
    def insert_match(tournament_id, round_, team1_id=None, team2_id=None, next_match_id=None):
        with session_factory() as session:
            new_match = MatchDB(
                tournament_id=tournament_id,
                round=round_,
                team1_id=team1_id,
                team2_id=team2_id,
                next_match_id=next_match_id,
                status=Status.IN_PROGRESS
            )
            session.add(new_match)
            session.commit()



Repository.create_tables()
UserRepository.insert_user("Alex Turner")
user_id = UserRepository.insert_user("Patric Jane")
tour_id = TournamentRepository.insert_tournament("test", user_id)
MatchRepository.insert_match(tour_id, 1, 1, 2)
MatchRepository.insert_match(tour_id, 2)