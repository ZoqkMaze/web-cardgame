const apiUrl = "127.0.0.1:8000/"

infoText = document.getElementById("serverData");
updateButton = document.getElementById("updateButton");

function getData() {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network error");
            }
            return response.json();
        })
        .then(data => {
            infoText.textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error("Error:", error);
        });
}

updateButton.addEventListener("click", getData);