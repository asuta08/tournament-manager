from fastapi import FastAPI
from schemas import UserSchema, TournamentSchema, MatchResultSchema
from service import Service

app = FastAPI()


@app.post("/users")
def create_user(user: UserSchema):
    user_id = Service.create_user(user.username)
    return {"user_id": user_id}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return Service.get_user(user_id)


@app.post("/tournaments")
def create_tournament(tournament: TournamentSchema):
    tournament_id = Service.create_tournament(tournament.user_id, tournament.name, tournament.teams)
    return {"tournament_id": tournament_id}

@app.get("/tournaments/{tournament_id}")
def get_tournament(tournament_id: int):
    return Service.get_tournament(tournament_id)

@app.get("/tournaments/{tournament_id}/bracket")
def get_tournament_bracket(tournament_id: int):
    return Service.get_bracket(tournament_id)

@app.get("/tournaments/{tournament_id}/winner")
def get_winner(tournament_id: int):
    winner_id = Service.get_tournament(tournament_id)["winner_id"]
    return {"winner_id": winner_id}


@app.get("/matches/{match_id}")
def get_match(match_id: int):
    return Service.get_match(match_id)

@app.post("/matches/{match_id}/result")
def apply_result(match_id: int, result: MatchResultSchema):
    Service.handle_match_result(match_id, result.team1_score, result.team2_score)
    return {"success": True}