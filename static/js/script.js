
document.getElementById('send-button').addEventListener('click', function() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (message) {
        addMessageToHistory(message, 'user');
        messageInput.value = '';

        const payload = JSON.stringify({ message: message });
        console.log("Sending JSON:", payload);  // Debugging log

        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: payload
        })
        .then(response => response.json())
        .then(data => {
            console.log("Response received:", data);  // Debugging log
            addMessageToHistory(data.response, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

// Add the event listener for the Enter key to send the message
var inputs = document.getElementsByTagName('input');
for (var i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            // Trigger the same action as clicking the send button
            document.getElementById('send-button').click();
        }
    });
}

function addMessageToHistory(message, sender) {
    const messageHistory = document.getElementById('message-history');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.textContent = message;
    messageHistory.appendChild(messageElement);
    messageHistory.scrollTop = messageHistory.scrollHeight;  // Scroll to the bottom
}

