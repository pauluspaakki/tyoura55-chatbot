const chatWindow = document.getElementById('chat-window');
const inputForm = document.getElementById('input-area');
const userInput = document.getElementById('user-input');

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

    // 2. Lisää "odotellaan..." -viesti (valinnainen, parantaa käyttökokemusta)
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot');
    loadingDiv.textContent = "Mietitään...";
    chatWindow.appendChild(loadingDiv);

    try {
        // 3. Lähetä viesti takahuoneeseen (Python-palvelimelle)
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // 4. Poista latausviesti ja lisää oikea vastaus
        chatWindow.removeChild(loadingDiv);
        addMessage(data.response, 'bot');

    } catch (error) {
        console.error('Virhe:', error);
        chatWindow.removeChild(loadingDiv);
        addMessage("Hups! Yhteys palvelimeen katkesi. Varmista, että Python-skripti pyörii.", 'bot');
    }
});
