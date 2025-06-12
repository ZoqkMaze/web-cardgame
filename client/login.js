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
const joinRandomButton = document.getElementById(joinRandomLobbyBtn);
const joinNormalButton = document.getElementById(joinLobbyByIdBtn)

createButton.addEventListener("click", () => {
    let name = lobbyNameInput.value;
    let playerCount = playerCountInput.value;
    let publicLobby = lobbyTypeInput.checked;
    console.log("creating lobby", name, playerCount, publicLobby);
    socket.emit("createLobby", name, playerCount, publicLobby);
});


socket.on("acceptLobby", () => {
    console.log("lobby creation succesfull!")
})


socket.on("refuseLobby", (msg) => {
    console.log(msg);
    createErrOutput.value = msg;
});
