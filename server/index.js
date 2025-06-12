const express = require("express");
const { createServer } = require("node:http");
const { join } = require("node:path");
const { Server } = require("socket.io");


const app = express();
const server = createServer(app);
const io = new Server(server, {
    connectionStateRecovery: {}
});

const hostname = '192.168.2.155';
const port = 3000;


// lobbies.name = room-name
const lobbies = {};  // {id: {name: str, public: true|false, full: true|false, size: int, host: player.id, players: [player.id], idle: bool, ...}}
const players = {};  // {id: {name: str, active: bool , lobby: lobby.id, human: bool}}
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


function registerPlayer(name, lobby_id=null, isHuman=true) {
    let player_id = generateId();
    players[player_id] = {"name": name, "active": true, "lobby": lobby_id, human: true};
    return player_id;
}


function createLobby(name, size, public, host) {
    let lobby_id = generateId();
    lobbies[lobby_id] = {"name": name, "public": public, "full": false, "size": Number(size), "host": host, "players": [host], "idle": true};
    return lobby_id;
}


function joinLobby(lobby_id, player_id) {
    if (lobby_id in lobbies && !lobbies[lobby_id].full && lobbies[lobby_id].idle) {
        lobbies[lobby_id].players.push(player_id);
        if (lobbies[lobby_id].size == lobbies[lobby_id].players.length) {
            lobbies[lobby_id].full = true;
        }
        players[player_id].lobby = lobby_id;
        return true;
    } else {
        return false;
    }
}


function redirectToLobby(socket, player_id, lobby_id, isHost=false) {
    // sockets[socket.id] = player_id; // geht nicht, da bei redirect neuer socket
    // socket.join(lobby_id); // fügt player zu raum hinzu
    socket.emit("joinLobby", player_id, lobby_id, isHost); // Benachichtigt client
    // Broadcast an Raum -> redirect schnell genug?
    io.to(lobby_id).emit("test");
}


function getLobbyData(lobby_id) {
    // [{name: str, host: bool, human: bool}]
    console.log("lobbies:", lobbies);
    console.log("players:", players);
    let array = []
    lobbies[lobby_id].players.forEach((player_id) => {
        console.log(player_id);
        array.push({
            "name": players[player_id].name,
            "host": player_id == lobbies[lobby_id].host,
            "human": players[player_id].human
        });
    });
    return [array, lobbies[lobby_id].size - array.length, lobbies[lobby_id].name];
}


function updateLobby(lobby_id, change, arg=null) {
    if (lobbies[lobby_id].idle) {
        switch (change) {
            case "leave":
                const index = lobbies[lobby_id].players.indexOf(arg)
                console.log(" > lobby before leave;", lobbies[lobby_id]);
                lobbies[lobby_id].players.splice(index, 1);
                console.log(" > lobby after leave;", lobbies[lobby_id]);
                lobbies[lobby_id].full = false;
                if (lobbies[lobby_id].players.length = 0) {
                    console.log(" > deleted lobby due to 0 players");
                    delete lobbies[lobby_id];
                } else if (lobbies[lobby_id].host == arg) {
                    console.log(" > changed host")
                    lobbies[lobby_id].host = lobbies[lobby_id].players[0];
                }
                break;
            case "join":
                joinLobby(lobby_id, arg);
                break;
        }
        io.to(lobby_id).emit("updateLobby", getLobbyData(lobby_id));
    }
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
        if (player_id in players) {
            sockets[socket.id] = player_id;
            players[player_id].active = true;
            if (! (players[player_id].lobby == null)) {
                socket.join(players[player_id].lobby);
                socket.emit("loggedIn");
            } else {
                socket.emit("reset");
            }
        } else {
            socket.emit("reset");
        }
    });

    socket.on("logOut", () => {  // mit player_id ?
        if (socket.id in sockets) {
            // lösche entsprechendne Spieler
            player_id = sockets[socket.id];
            lobby_id = players[player_id].lobby;
            updateLobby(lobby_id, "leave", player_id);
            delete players[player_id];
            socket.leave(lobby_id);
        }
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
                redirectToLobby(socket, player_id, lobby_id, true);
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
                if (lobbies[id].public && !lobbies[id].full && lobbies[id].idle) {
                    lobby_id = id;
                    break;
                }
            }
            if (lobby_id == null) {
                socket.emit("refuseJoin", "no open lobby");
            } else {
                const player_id = registerPlayer(player_name, lobby_id);
                //const success = joinLobby(lobby_id, player_id);
                updateLobby(lobby_id, "join", player_id);
                const success = true;
                if (success) {
                    redirectToLobby(socket, player_id, lobby_id);
                } else {
                    socket.emit("refuseJoin", "unexpected error");
                }
            }
        } else {
            socket.emit("refuseJoin", "invalid user name");
        }
    });

    socket.on("codeJoin", (player_name, lobby_id) => {
        if (nameIsValid(player_name)) {
            // lobby mit id und freien Plätzen?
            if (lobby_id in lobbies) {
                if (lobbies[lobby_id].full || !(lobbies[lobby_id].idle)) {
                    socket.emit("refuseJoin", "lobby is full");
                } else {
                    // player zu lobby hinzufügen
                    const player_id = registerPlayer(player_name, lobby_id);
                    //const success = joinLobby(lobby_id, player_id);
                    updateLobby(lobby_id, "join", player_id);
                    const success = true;
                    if (success) {
                        redirectToLobby(socket, player_id, lobby_id);
                    } else {
                        socket.emit("refuseJoin", "unexpected error");
                    }
                }
            } else {
                socket.emit("refuseJoin", "no lobby with given id");
            }
        } else {
            socket.emit("refuseJoin", "invalid user name");
        }
    });

    socket.on("requestUpdateLobby", (player_id, lobby_id) => {
        if (lobby_id in lobbies) {
            if (lobbies[lobby_id].players.includes(player_id)) {
                socket.emit("updateLobby", getLobbyData(lobby_id));
            } else {
                socket.emit("reset");
            }
        } else {
            socket.emit("reset");
        }
    });

    socket.on("leaveLobby", (player_id) => { // todo: alle weg nach leave
        lobby_id = players[player_id].lobby;
        updateLobby(lobby_id, "leave", player_id);
        delete players[player_id];
    })

    socket.on("disconnect", () => {
        // todo: disconnect richtig verarbeiten!
        console.log("user logged out:", socket.id);
        if (socket.id in sockets) {
            player_id = sockets[socket.id]
            if (player_id in players) {
                players[player_id].active = false;
            }
            delete sockets[socket.id];
        }
    });
});

server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`)
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