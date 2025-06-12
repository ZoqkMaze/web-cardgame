const socket = io();

const player_id = localStorage.getItem("player_id");
const lobby_id = localStorage.getItem("lobby_id");
const isHost = localStorage.getItem("host") == 'true';

const lobbyNameHeading = document.getElementById("lobbyName");
const playerList = document.getElementById("playersList");
const hostButtons = document.getElementById("hostOptions");

const addButton = document.getElementById("addSlotBtn");
const startButton = document.getElementById("startGameBtn");
const leaveButton = document.getElementById("leaveLobbyBtn");

if (!isHost) {
    hostButtons.classList.add("disabled-container");
}

leaveButton.addEventListener("click", () => {
    socket.emit("leaveLobby", player_id);
    localStorage.removeItem("player_id");
    localStorage.removeItem("lobby_id");
    localStorage.removeItem("host");
    window.location.href = "/";
});


function atLeatsOnesEmit(event, arg) {
    socket.timeout(5000).emit(event, arg, (err) => {
        if (err) {
            atLeatsOnesEmit(event, arg);
        }
    });
}


function createLi(name, host, human, empty) {
    const li = document.createElement("li");

    const div1 = document.createElement("div");
    const span1 = document.createElement("span");
    span1.classList.add("playerName");
    span1.innerHTML = name;
    div1.appendChild(span1);
    if (host) {
        const span = document.createElement("span");
        span.classList.add("host-badge");
        span.innerHTML = "Host";
        div1.appendChild(span);
    }
    li.appendChild(div1);

    const div2 = document.createElement("div");
    div2.classList.add("slot-controls")
    const span2 = document.createElement("span");
    span2.classList.add("slot-type");
    if (empty) {
        span2.innerHTML = "Leer";
    } else {
        span2.innerHTML = human ? "Spieler" : "Computer";
    }
    div2.appendChild(span2);
    if (isHost) {
        if (empty) {
            const b1 = document.createElement("button");
            b1.classList.add("kick-btn");
            b1.title = "Platz löschen";
            b1.innerHTML = "✖";
            div2.appendChild(b1);

            const b2 = document.createElement("button");
            b2.classList.add("kick-btn");
            b2.title = "zu Computer";
            b2.innerHTML = "🤖";
            div2.appendChild(b2);
        } else if (!host) {
            const b = document.createElement("button");
            b.classList.add("kick-btn");
            b.title = "Spieler kicken";
            b.innerHTML = "Kick";
            div2.appendChild(b);
        }
    }

    li.appendChild(div2);

    playerList.appendChild(li);
}

console.log("Try to login");
socket.emit("logIn", player_id);  // atLeatsOnes?
socket.emit("requestUpdateLobby", player_id, lobby_id);  // atLeatsOnes?

socket.on("reset", () => {
    localStorage.clear();
    window.location.href = "/index.html";
});

socket.on("loggedIn", () => {
    console.log("login succesfull");
})

socket.on("updateLobby", (updataData) => {
    // updateData: [{name: str, host: bool, human: bool}]
    console.log("updateData:", updataData);
    playerList.replaceChildren();
    updataData[0].forEach(player => {
        createLi(player.name, player.host, player.human, false);
    });
    for (let i = 0; i < updataData[1]; i++) {
        createLi("", false, true, true);
    }
    lobbyNameHeading.innerHTML = updataData[2] + " (" + lobby_id + ")";
});