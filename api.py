from fastapi import FastAPI
from classes import *
import uuid  # for player ids
from nanoid import generate  # for lobby ids


UNKNOWN_PLAYER_ERROR = {"error": "Unknown player_id"}
UNKNOWN_GAME_ERROR = {"error": "Unknown game_id"}
UNKNOWN_CARD_ERROR = {"error": "Unknown card_id"}


def get_player_name(name):
    return f"User{generate("0123456789", 5)}" if name is None else name

def create_player_id():
    return str(uuid.uuid1())

def create_game_id():
    return generate(size=8)


class WebUser(Player):

    def __init__(self, id, name):
        self.name: str = name
        self.lobby_id: str = None
        super().__init__(id)
    
    @property
    def status_json(self):
        return {
            "player_id": self.id,
            "name": self.name,
            "game_id": self.lobby_id,
            "total_points": self.total_game_score,
        }


app = FastAPI()

players: dict[str, WebUser] = dict()

lobbies: dict[str, GameManager] = dict()


@app.get("/")
async def root():
    return {"info": "Welcome to the Witches API! If you are new, a look at /docs could be helpfull."}

@app.get("/join/{game_id}")
async def join_game(game_id: str, name: str | None = None):
    if game_id in lobbies:
        new_id = create_player_id()
        new_name = get_player_name(name)
        new_player = WebUser(new_id, new_name)
        if lobbies[game_id].join(new_player):
            return {"error": "unable to join lobby"}
        new_player.lobby_id = game_id
        players[new_id] = new_player
        return {"status": "successfully joined game", "player_id": new_id, "game_id": game_id}
    return UNKNOWN_GAME_ERROR

@app.get("/create")
async def create_game(name: str | None = None):
    game_id = create_game_id()
    player_id = create_player_id()
    while game_id in lobbies or player_id in players:
        game_id = create_game_id()
        player_id = create_player_id()

    player = WebUser(player_id, get_player_name(name))
    manager = GameManager(game_id)

    if manager.join(player):
        return {"error": "unable to create lobby"}
    
    player.lobby_id = game_id
    players[player_id] = player
    lobbies[game_id] = manager
    return {"status": "successfully created game", "player_id": player_id, "game_id": game_id}

@app.get("/player/{player_id}")
async def player_request(player_id: str):
    if player_id in players:
        return {"type": "player"} | players[player_id].status_json
    return UNKNOWN_PLAYER_ERROR

@app.get("/game/{game_id}")
async def game_request(game_id: str):
    if game_id in lobbies:
        return {"type": "game"} | lobbies[game_id].status_json | {"players": [ players[p_id].name for p_id in lobbies[game_id].player_ids ]}
    return UNKNOWN_GAME_ERROR

@app.get("/leave/{player_id}")
async def leave_game(player_id: str):
    if not player_id in players:
        return UNKNOWN_PLAYER_ERROR
    lobby_id = players[player_id].lobby_id
    lobby = lobbies[lobby_id]
    lobby.leave_by_id(player_id)
    del players[player_id]
    if not lobby.player_count:
        del lobbies[lobby_id]

@app.get("/cards/{player_id}")
async def show_cards(player_id: str):
    if player_id not in players:
        return UNKNOWN_PLAYER_ERROR
    return

@app.get("/play_card/{player_id}")
async def play_card(player_id: str, card_id: str):
    if player_id not in players:
        return UNKNOWN_PLAYER_ERROR
    player = players[player_id]
    if card_id not in player.card_ids:
        return UNKNOWN_CARD_ERROR