from fastapi import FastAPI
from classes import *


app = FastAPI()

player_dict: dict[str, Player] = {f"p{i}": Player(f"p{i}") for i in range(4)}

lobby_dict: dict[str, GameManager] = {f"g{i}": GameManager(f"g{i}") for i in range(2)}


@app.get("/")
async def root():
    return {"info": "Welcome to the Witches API! If you are new, a look at /docs could be helpfull."}

@app.get("/test/{param}")
async def test(param: int, foo: float | None = None):
    return {"site": "test", "param": param, "foo": foo}

@app.get("/player/{player_id}")
async def player_request(player_id: str):
    if player_id in player_dict:
        return {"type": "player"} | player_dict[player_id].status_json
    return {"error": "Unknown player"}

@app.get("/game/{game_id}")
async def handle_game_reqest(game_id: str):
    if game_id in lobby_dict:
        return {"type": "game"} | lobby_dict[game_id].status_json
    return {"error": "Unknown game"}