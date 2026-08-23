from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from tournament import Status


class UserDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]

    tournaments: Mapped[List["TournamentDB"]] = relationship(
        "TournamentDB",
        back_populates="creator"
    )


class TournamentDB(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[Status]
    winner_id: Mapped[int | None]

    creator: Mapped["UserDB"] = relationship(
        "UserDB",
        back_populates="tournaments"
    )

    matches: Mapped[List["MatchDB"]] = relationship(
        "MatchDB",
        back_populates="tournament"
    )


class MatchDB(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"))
    round: Mapped[int]
    team1_id: Mapped[int | None]
    team2_id: Mapped[int | None]
    team1_score: Mapped[int | None]
    team2_score: Mapped[int | None]
    winner_id: Mapped[int | None]
    status: Mapped[Status]
    next_match_id: Mapped[int | None]

    tournament: Mapped["TournamentDB"] = relationship(
        "TournamentDB",
        back_populates="matches"
    )