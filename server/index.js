const express = require("express");
const { createServer } = require("node:http");
const { join } = require("node:path");
const { Server } = require("socket.io");


const app = express();
const server = createServer(app);
const io = new Server(server, {
    connectionStateRecovery: {}
});


// lobbies.name = room-name
const lobbies = {};  // {id: {name: str, public: true|false, full: true|false, size: int, host: player.id, players: [player.id], ...}}
const players = {};  // {id: {name: str, active: bool , lobby: lobby.id}}
const sockets = {};  // {socket.id: player.id};

/*
function generateId() {
  return 'id-' + Date.now().toString(36) + '-' + Math.random().toString(36).substring(2, 5);
}
  */

function generateId(length = 6) {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let id = '';
    for (let i = 0; i < length; i++) {
        id += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return id;
}


function nameIsValid(name) {
    // lobby_name is key of lobbies; only alphanumeric
    if (/^[a-zA-Z0-9]+$/.test(name)) {
        return true;
    } else {
        return false;
    }
};


function registerPlayer(name, lobby_id=null) {
    let player_id = generateId();
    players[player_id] = {"name": name, "active": true, "lobby": lobby_id};
    return player_id;
}


function createLobby(name, size, public, host) {
    let lobby_id = generateId();
    lobbies[lobby_id] = {"name": name, "public": public, "full": false, "size": size, "host": host, "players": [host]};
    return lobby_id;
}


function joinLobby(lobby_id, player_id) {
    if (lobby_id in lobbies && !lobbies[lobby_id].full) {
        lobbies[lobby_id].players.push(player_id);
        if (lobbies[lobby_id].size = lobbies[lobby_id].players.length) {
            lobbies[lobby_id].full = true;
        }
        players[player_id].lobby = lobby_id;
    }
}


function redirectToLobby(socket, player_id, lobby_id) {
    sockets[socket.id] = player_id; // fals disconnect
    socket.join(lobby_id); // fügt player zu raum hinzu
    socket.emit("joinLobby", player_id, lobby_id); // Benachichtigt client
}


app.use(express.static(join(__dirname, "..", "client")));

/*
app.get('/start', (req, res) => {
  const lobbyId = "abc123"; // Beispiel
  res.redirect(`/lobby/${lobbyId}`);
});
*/


// neuer client verbindet sich 
io.on("connection", (socket) => {
    console.log("user logged in:", socket.id);

    socket.on("logIn", (player_id) => {
        // stelle player nach disconnect wieder auf active
    });

    socket.on("createLobby", (user_name, lobby_name, playerCount, publicLobby) => {
        console.log(`user ${user_name} requested lobby ${lobby_name} (${playerCount}, ${publicLobby})`);
        if (playerCount < 3 || playerCount > 6) {
            socket.emit("refuseLobby", "invalid lobby size");
            console.log("refused lobby: wrong lobby size");
        } else if (!nameIsValid(user_name)) {
            console.log("refused lobby: unvalid user name");
            socket.emit("refuseLobby", "invalid user name");
        } else {
            if (nameIsValid(lobby_name)) {
                // erzeuge lobby + leite user weiter
                let player_id = registerPlayer(user_name);
                let lobby_id = createLobby(lobby_name, playerCount, publicLobby, player_id);
                players[player_id].lobby = lobby_id;
                console.log("accepted lobby", lobby_id);
                redirectToLobby(socket, player_id, lobby_id);
            } else {
                // erstellunbg ablehnen
                console.log("refused lobby: invalid lobby name")
                socket.emit("refuseLobby", "invalid lobby name");
            }
        }
    });

    socket.on("randomJoin", (player_name) => {
        if (nameIsValid(player_name)) {
            // public lobby mit freien Plätzen?
            let lobby_id = null;
            for (const id in lobbies) {
                if (lobbies[id].public && !lobbies[id].full) {
                    lobby_id = id;
                    break;
                }
            }
            if (lobby_id == null) {
                socket.emit("refuseJoin", "no open lobby");
            } else {
                const player_id = registerPlayer(player_name, lobby_id);
                joinLobby(lobby_id, player_id);
                redirectToLobby(socket, player_id, lobby_id);
            }
        } else {
            socket.emit("refuseJoin", "invalid user name");
        }
    });

    socket.on("codeJoin", (player_name, lobby_id) => {
        if (nameIsValid(player_name)) {
            // lobby mit id und freien Plätzen?
            if (lobby_id in lobbies) {
                if (lobbies[lobby_id].full) {
                    socket.emit("refuseJoin", "lobby is full");
                } else {
                    // player zu lobby hinzufügen
                    const player_id = registerPlayer(player_name, lobby_id);
                    joinLobby(lobby_id, player_id);
                    redirectToLobby(socket, player_id, lobby_id);
                }
            } else {
                socket.emit("refuseJoin", "no lobby with given id");
            }
        } else {
            socket.emit("refuseJoin", "invalid user name");
        }
    });

    socket.on("disconnect", () => {
        console.log("user logged out:", socket.id);
        if (socket.id in sockets) {
            players[sockets[socket.id]].active = false;
            delete sockets[socket.id];
        }
    });
});

server.listen(3000, () => {
    console.log("server running at localhost:3000")
});


    //socket.join("room");
    //io.to("room").emit("...");
    //socket.leave("room");
//
    //// neues Event eingegangen -> handling
    //socket.on("eventName", (value) => {
    //    console.log(value);
    //    io.emit("event", value);  // brodcast to all
    //    // io.brodcast.emit(...); // alle außer der Sender
    //});