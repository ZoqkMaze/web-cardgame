// show status
// start game
// monitore game status and display change
// when should the client update info? or should the server inform about changes?

const apiURL = "http://127.0.0.1:8000/"

const playerID = localStorage.getItem("playerId");
const lobbyID = localStorage.getItem("lobbyId");

const lobby = {
    version: 0,
    players: [],
    state: "join",
    round: 0,
}

let playerList = document.getElementById("playerList");
let lobbyStatusText = document.getElementById("gameStatus");

async function needUpdate() {
    return fetch(apiURL+"version/"+lobbyID)
        .then(async response => {
            const body = await response.json()
            if (!body.success) {
                return false;
            }
            if (lobby.version == body.version) {
                return false;
            } 
            lobby.version = body.version;
            return true;
        });
}

function renderLobbyData() {
    playerList.innerHTML = "";
    lobby.players.forEach( (element) => {
        li = document.createElement("li")
        li.textContent = element;
        playerList.appendChild(li);
    });
    lobbyStatusText.textContent = "state: " + lobby.state
}

async function updateLobby() {
    if (!await needUpdate()) {
        console.log("DONT NEED!");
        return
    }
    await fetch(apiURL+"lobby/"+lobbyID)
        .then(async response => {
            const body = await response.json()
            if (!body.success) {
                return
            }
            lobby.players = body.players;
            lobby.state = body.state;
            lobby.round = body.round;
        });
    renderLobbyData();
}

setInterval(updateLobby, 1000);