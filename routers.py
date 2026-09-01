from fastapi import APIRouter
from fastapi.params import Depends

from dependencies import get_current_user
from exceptions import AuthError
from schemas import TournamentSchema, MatchResultSchema, UserAuthSchema
from security import hash_password, verify_password, create_token
from service import Service

router = APIRouter()


@router.post("/auth/register")
def register_user(user: UserAuthSchema):
    hashed_password = hash_password(user.password)
    user_id = Service.create_user(user.username, hashed_password)
    return {"user_id": user_id}

@router.post("/auth/login")
def login_user(user: UserAuthSchema):
    data = Service.get_user_by_username(user.username)

    if not verify_password(user.password, data["hashed_password"]):
        raise AuthError("Invalid password!", 401)

    return {"access_token": create_token(data["user_id"])}


@router.post("/tournaments", status_code=201, tags=["Tournaments"], summary="Create a new tournament")
def create_tournament(tournament: TournamentSchema, user_id: int = Depends(get_current_user)):
    tournament_id = Service.create_tournament(user_id, tournament.name, tournament.teams)
    return {"tournament_id": tournament_id}

@router.get("/tournaments/{tournament_id}", tags=["Tournaments"], summary="Get tournament by id")
def get_tournament(tournament_id: int, _: None = Depends(get_current_user)):
    return Service.get_tournament(tournament_id)

@router.get("/tournaments/{tournament_id}/bracket", tags=["Tournaments"], summary="Get tournament bracket by id")
def get_tournament_bracket(tournament_id: int, _: None = Depends(get_current_user)):
    return Service.get_bracket(tournament_id)

@router.get("/tournaments/{tournament_id}/winner", tags=["Tournaments"], summary="Get tournament winner")
def get_winner(tournament_id: int, _: None = Depends(get_current_user)):
    winner_id = Service.get_tournament(tournament_id)["winner_id"]
    return {"winner_id": winner_id}


@router.get("/matches/{match_id}", tags=["Matches"], summary="Get match by id")
def get_match(match_id: int, _: None = Depends(get_current_user)):
    return Service.get_match(match_id)

@router.post("/matches/{match_id}/result", status_code=201, tags=["Matches"], summary="Add a match result")
def apply_result(match_id: int, result: MatchResultSchema, _: None = Depends(get_current_user)):
    Service.handle_match_result(match_id, result.team1_score, result.team2_score)
    return {"success": True}