import socket from "./socket.js";

// player info
const playerNameInput = document.getElementById("playerName");

// create lobbby info
const lobbyNameInput = document.getElementById("lobbyName");
const playerCountInput = document.getElementById("maxPlayers");
const lobbyTypeInput = document.getElementById("isPublic");
const createButton = document.getElementById("createLobbyBtn");
const createErrOutput = document.getElementById("createLobbyErrors");

// join info
const joinRandomButton = document.getElementById("joinRandomLobbyBtn");
// const randomErrOutput = document.getElementById("randomLobbyErrors");
const lobbyIdInput = document.getElementById("lobbyId");
const joinNormalButton = document.getElementById("joinLobbyByIdBtn");
const joinErrOutput = document.getElementById("joinLobbyErrors");

createButton.addEventListener("click", () => {
    let player_name = playerNameInput.value;
    let lobby_name = lobbyNameInput.value;
    let playerCount = playerCountInput.value;
    let publicLobby = lobbyTypeInput.checked;
    console.log("creating lobby", lobby_name, playerCount, publicLobby);
    socket.emit("createLobby", player_name, lobby_name, playerCount, publicLobby);
});

joinRandomButton.addEventListener("click", () => {
    let player_name = playerNameInput.value;
    console.log("try random join");
    socket.emit("randomJoin", player_name);
});

joinNormalButton.addEventListener("click", () => {
    let player_name = playerNameInput.value;
    let lobby_id = lobbyIdInput.value;
    console.log("try to join lobby", lobby_id);
    socket.emit("codeJoin", player_name, lobby_id);
});


socket.on("joinLobby", (player_id, lobby_id) => {
    console.log(`${player_id} joind ${lobby_id}`);
    localStorage.setItem("player_id", player_id);
    localStorage.setItem("lobby_id", lobby_id);
    // Weiterleitung zur Lobby
    window.location.href = "/lobby.html";
});


socket.on("refuseLobby", (msg) => {
    console.log(msg);
    createErrOutput.innerHTML = msg;
});

socket.on("refuseJoin", (msg) => {
    console.log(msg);
    joinErrOutput.innerHTML = msg;
});
