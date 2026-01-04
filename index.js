const apiUrl = "http://127.0.0.1:8000/"

infoText = document.getElementById("serverData");
errorText = document.getElementById("errorLog");

lobbyInput = document.getElementById("lobbyInput");
nameInput = document.getElementById("nameInput");

joinButton = document.getElementById("joinButton");
createButton = document.getElementById("createButton");

function createLobby() {
    fetch(apiUrl+"create?name="+nameInput.value)
        .then(async response => {
            const body = await response.json();
            if (!body.success) {
                errorText.textContent = body.message;
                return;
            }
            infoText.textContent = body.message;
            localStorage.setItem("playerId", body.player_id);
            // redirect to lobby
            window.location.assign("lobby.html");
        });
}

function joinLobby() {
    // random public lobby or specific lobby via code
    lobbyId = lobbyInput.value;
    if (lobbyId.length > 1) {
        fetch(apiUrl+"join/"+lobbyId+"?name="+nameInput.value)
        .then(async response => {
            const body = await response.json();
            if (!body.success) {
                errorText.textContent = body.message;
                return;
            }
            infoText.textContent = body.message;
            localStorage.setItem("playerId", body.player_id);
            // redirect to lobby
            window.location.assign("lobby.html");
        })
    } else {
        // random join not implemented jet
        errorText.textContent = "please insert a valid lobby id";
    }
}


joinButton.addEventListener("click", joinLobby);
createButton.addEventListener("click", createLobby);