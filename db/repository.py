from typing import List

from db.database import Base, engine, session_factory

from models import UserDB, TournamentDB, MatchDB
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

            session.commit()



Repository.create_tables()
UserRepository.insert_user("Alex Turner")
user_id = UserRepository.insert_user("Patric Jane")
tour_id = TournamentRepository.insert_tournament("test", user_id)


# test_tournament = Tournament("test", [1, 2, 3, 4, 5, 6, 7, 8])
# test_tournament.create_bracket()
# MatchRepository.insert_bracket(tour_id, test_tournament.bracket)

# tour2_id = TournamentRepository.insert_tournament("test2", user_id)
# test_tournament2 = Tournament("test2", [1, 2, 3, 4, 5])
# test_tournament2.create_bracket()
# MatchRepository.insert_bracket(tour2_id, test_tournament2.bracket)

test_tournament = Tournament("test", [1, 2, 3, 4])
test_tournament.create_bracket()
MatchRepository.insert_bracket(tour_id, test_tournament.bracket)

team_id = test_tournament.bracket[0].team1_id
m_id = test_tournament.handle_result(team_id)
MatchRepository.update_after_result(m_id, 3, 2, team_id)
team_id = test_tournament.bracket[1].team1_id
m_id = test_tournament.handle_result(team_id)
MatchRepository.update_after_result(m_id, 3, 2, team_id)
TournamentRepository.update_current_round(1)
m_id = test_tournament.handle_result(team_id)
MatchRepository.update_after_result(m_id, 3, 2, team_id)