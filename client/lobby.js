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

playerList = document.getElementById("playerList");
lobbyStatusText = document.getElementById("gameStatus");

function needUpdate() {
    let result = false;
    fetch(apiURL+"version/"+lobbyID)
        .then(response => {
            if (!response.success) {
                return;
            }
            if (lobby.version == response.version) {
                return;
            } 
            lobby.version = response.version;
            result = true;
        });
    return result;
}

function renderLobbyData() {
    playerList.innerHTML = "";
    playerList.forEach(element => {
        li = document.createElement("li")
        li.textContent = element;
        playerList.appendChild(li);
    });
    lobbyStatusText.textContent = "state: " + lobby.state
}

function updateLobby() {
    if (!needUpdate()) {
        return
    }
    fetch(apiURL+"lobby/"+lobbyID)
        .then(response => {
            if (!response.success) {
                return
            }
            lobby.players = response.players;
            lobby.state = response.state;
            lobby.round = response.round;
        });
    renderLobbyData();
}

setInterval(updateLobby, 1000);