from fastapi import APIRouter
from fastapi.params import Depends

from app.api.dependencies import get_current_user
from app.core.exceptions import AuthError
from app.schemas import TournamentSchema, MatchResultSchema, UserAuthSchema
from app.api.security import hash_password, verify_password, create_token
from app.service import Service

router = APIRouter()


@router.post("/auth/register", status_code=201, tags=["Authentication"])
def register_user(user: UserAuthSchema):
    hashed_password = hash_password(user.password)
    user_data = Service.get_user_by_username(user.username)

    if user_data is not None:
        raise AuthError("User is already registered!", 400)

    user_id = Service.create_user(user.username, hashed_password)
    return {"user_id": user_id}

@router.post("/auth/login", tags=["Authentication"])
def login_user(user: UserAuthSchema):
    user_data = Service.get_user_by_username(user.username)

    if user_data is None:
        raise AuthError("User is not registered!", 401)

    if not verify_password(user.password, user_data["hashed_password"]):
        raise AuthError("Invalid password!", 401)

    return {"access_token": create_token(user_data["user_id"])}


@router.get("/users/me", tags=["Users"], summary="Get yourself")
def get_me(user_id: int = Depends(get_current_user)):
    return Service.get_user(user_id)


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

@router.patch("/matches/{match_id}/result", tags=["Matches"], summary="Add a match result")
def apply_result(match_id: int, result: MatchResultSchema, _: None = Depends(get_current_user)):
    Service.handle_match_result(match_id, result.team1_score, result.team2_score)
    return {"success": True}