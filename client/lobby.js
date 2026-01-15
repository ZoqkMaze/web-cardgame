// show status
// start lobby
// monitore lobby status and display change
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

let playerListElement = document.getElementById("playerList");
let lobbyStatusText = document.getElementById("lobbyStatus");
document.getElementById("lobbyId").textContent = "lobby id: " + lobbyID;
let startButton = document.getElementById("startButton");

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
    playerListElement.innerHTML = "";
    lobby.players.forEach( (element) => {
        li = document.createElement("li")
        li.textContent = element;
        playerListElement.appendChild(li);
    });
    lobbyStatusText.textContent = "state: " + lobby.state
}

async function updateLobby() {
    if (!await needUpdate()) {
        // console.log("DONT NEED!");
        return
    }
    await fetch(apiURL+"lobby/"+lobbyID)
        .then(async response => {
            const body = await response.json();
            if (!body.success) {
                return
            }
            lobby.players = body.players;
            lobby.state = body.state;
            lobby.round = body.round;
        });
    renderLobbyData();
}

async function startGame() {
    console.log("start game");
    await fetch(apiURL + "start/"+playerID)
        .then(async response => {
            const body = await response.json();
            if (body.success) {
                console.log("successfully started game");
            } else {
                console.log("error when starting game");
            }
        });
}

setInterval(updateLobby, 1000);

startButton.addEventListener("click", startGame);