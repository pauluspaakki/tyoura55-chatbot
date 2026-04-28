const chatWindow = document.getElementById('chat-window');
const inputForm = document.getElementById('input-area');
const userInput = document.getElementById('user-input');
const pdfInput = document.getElementById('pdf-input');
const uploadBtn = document.getElementById('upload-btn');

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    div.textContent = text;
    chatWindow.appendChild(div);

    // Vieritä automaattisesti alas
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

inputForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();

    if (!message) return;

    // 1. Lisää käyttäjän viesti näkyviin
    addMessage(message, 'user');
    userInput.value = '';

    // 2. Lisää "odotellaan..." -viesti
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot');
    loadingDiv.textContent = "Mietitään...";
    chatWindow.appendChild(loadingDiv);

    try {
        // 3. Lähetä viesti takahuoneeseen (Python-palvelimelle)
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                user_id: "user123"
            })
        });

        const data = await response.json();

        const responseText = data.response;

        if (
            responseText.toLowerCase().includes("lähetä pdf-tiedosto")) {
            showUpload();
        } else {
            hideUpload();
        }

        // 4. Poista latausviesti ja lisää oikea vastaus
        chatWindow.removeChild(loadingDiv);
        addMessage(responseText, 'bot');

    } catch (error) {
        console.error('Virhe:', error);
        chatWindow.removeChild(loadingDiv);
        addMessage("Hups! Yhteys palvelimeen katkesi. Varmista, että Python-skripti pyörii.", 'bot');
    }
});

// lataa pdf-tiedosto
async function uploadPdf(file) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", "user123");

    const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    addMessage(data.response || "Pdf käsitelty", 'bot');

    hideUpload();
}

uploadBtn.addEventListener('click', () => {
    const file = document.getElementById("pdf-input").files[0];

    if (!file) {
        alert("Valitse pdf!");
        return;
    }

    uploadPdf(file);
});

function showUpload() {
    document.getElementById("pdf-upload").style.display = "block";
};

function hideUpload() {
    document.getElementById("pdf-upload").style.display = "none";
};

window.onload = async () => {
    console.log("start call");

    const res = await fetch("http://127.0.0.1:5000/start?user_id=user123");
    const data = await res.json();

    addMessage(data.response, "bot");
};
