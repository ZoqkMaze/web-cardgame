from fastapi import FastAPI
from classes import *


class WebPlayer(Player):
    def __init__(self, p_id):
        self.id = p_id
        super().__init__()

    def choose_card(self):
        return super().choose_card()

app = FastAPI()

player_dict: dict[str, Player] = {f"p{i}": WebPlayer(f"p{i}") for i in range(4)}

game_dict: dict[str, Game] = {
    "myFirstGame": Game(list(player_dict.values())[:4])
}


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