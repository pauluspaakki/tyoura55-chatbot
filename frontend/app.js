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

inputForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = userInput.value.trim();

    if (message) {
        // Käyttäjän viesti
        addMessage(message, 'user');
        userInput.value = '';

        // Simuloitu botin vastaus (viiveellä)
        setTimeout(() => {
            addMessage("Vastaanotin viestisi: " + message, 'bot');
        }, 1000);
    }
});