const express = require("express");
const { createServer } = require("node:http");
const { join } = require("node:path");
const { Server } = require("socket.io");


const app = express();
const server = createServer(app);
const io = new Server(server, {
    connectionStateRecovery: {}
});

const lobbies = {};


function nameIsValid(name) {
    if (/^[a-zA-Z0-9]+$/.test(name) && !(name in lobbies)) {
        return true;
    } else {
        return false;
    }
}

app.use(express.static(join(__dirname, "..", "client")));


// neuer client verbindet sich 
io.on("connection", (socket) => {
    console.log("user logged in");

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

    socket.on("createLobby", (name, playerCount, publicLobby) => {
        console.log("user requested lobby", name, playerCount, publicLobby);
        if (nameIsValid(name)) {
            // erzeuge lobby + leite user weiter
            socket.emit("acceptLobby");
        } else {
            // erstellunbg ablehnen
            socket.emit("refuseLobby", "invalid lobby name");
        }
    });

    socket.on("disconnect", () => {
        console.log("user logged out");
    });
});

server.listen(3000, () => {
    console.log("server running at localhost:3000")
});