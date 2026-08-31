from fastapi import APIRouter

from exceptions import AuthError
from schemas import UserSchema, TournamentSchema, MatchResultSchema
from security import hash_password, verify_password, create_token
from service import Service

router = APIRouter()


@router.post("/auth/register")
def register_user(user: UserSchema):
    hashed_password = hash_password(user.password)
    user_id = Service.create_user(user.username, hashed_password)
    return {"user_id": user_id}

@router.post("/auth/login")
def login_user(user: UserSchema):
    data = Service.get_user_by_username(user.username)

    if not verify_password(user.password, data["hashed_password"]):
        raise AuthError("Invalid password!", 401)

    return {"access_token": create_token(data["user_id"])}

# @router.post("/users", status_code=201, tags=["Users"], summary="Create a new user")
# def create_user(user: UserSchema):
#     user_id = Service.create_user(user.username)
#     return {"user_id": user_id}

# @router.get("/users/{user_id}", tags=["Users"], summary="Get user by id")
# def get_user(user_id: int):
#     return Service.get_user(user_id)


@router.post("/tournaments", status_code=201, tags=["Tournaments"], summary="Create a new tournament")
def create_tournament(tournament: TournamentSchema):
    tournament_id = Service.create_tournament(tournament.user_id, tournament.name, tournament.teams)
    return {"tournament_id": tournament_id}

@router.get("/tournaments/{tournament_id}", tags=["Tournaments"], summary="Get tournament by id")
def get_tournament(tournament_id: int):
    return Service.get_tournament(tournament_id)

@router.get("/tournaments/{tournament_id}/bracket", tags=["Tournaments"], summary="Get tournament bracket by id")
def get_tournament_bracket(tournament_id: int):
    return Service.get_bracket(tournament_id)

@router.get("/tournaments/{tournament_id}/winner", tags=["Tournaments"], summary="Get tournament winner")
def get_winner(tournament_id: int):
    winner_id = Service.get_tournament(tournament_id)["winner_id"]
    return {"winner_id": winner_id}


@router.get("/matches/{match_id}", tags=["Matches"], summary="Get match by id")
def get_match(match_id: int):
    return Service.get_match(match_id)

@router.post("/matches/{match_id}/result", status_code=201, tags=["Matches"], summary="Add a match result")
def apply_result(match_id: int, result: MatchResultSchema):
    Service.handle_match_result(match_id, result.team1_score, result.team2_score)
    return {"success": True}