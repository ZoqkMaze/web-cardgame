from fastapi import FastAPI
from classes import *


app = FastAPI()

player_dict: dict[str, Player] = {f"p{i}": Player(f"p{i}") for i in range(4)}

lobby_dict: dict[str, ]


@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/test/{param}")
async def test(param: int, foo: float | None = None):
    return {"site": "test", "param": param, "foo": foo}

@app.get("/player/{player_id}")
async def player_request(player_id: str):
    if player_id in player_dict:
        return {"player": player_id}
    return {"error": "unknown player"}

@app.get("/game/{game_id}")
async def handle_game_reqest(game_id: str):
    if game_id in game_dict:
        return {"id": game_id} | game_dict[game_id].game_status()
    return {"detail": "Not Found"}