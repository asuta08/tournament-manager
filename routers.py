from fastapi import FastAPI
from schemas import UserSchema
from service import Service

app = FastAPI()

@app.post("/users")
def create_user(user: UserSchema):
    user_id = Service.create_user(user.username)
    return {"user_id": user_id}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return Service.get_user(user_id)