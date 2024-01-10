let lastUserMessage = "";  // Track the last user message

async function sendToRasa(message) {
    try {
        const response = await fetch("http://localhost:5005/webhooks/rest/webhook", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sender: "user",
                message: message
            })
        });

        const data = await response.json();

        if (data && data.length > 0 && data[0].text) {
            return data[0].text;
        } else {
            console.error("Unexpected Rasa response:", data);
            return "Sorry, I didn't understand that.";
        }

    } catch (error) {
        console.error("Error communicating with Rasa:", error);
        return "Sorry, I encountered an error.";
    }
}

function handleEnter(e) {
    if (e.keyCode === 13 && e.target.value.trim() !== "") {
        e.preventDefault();
        sendMessage();
    }
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    if (input.value.trim() !== "") {
        const userMessageText = input.value.trim();

        lastUserMessage = userMessageText;

        const userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        userMessage.innerText = userMessageText;
        chatBox.appendChild(userMessage);

        sendToRasa(userMessageText).then(botReply => {
            const botMessage = document.createElement('div');
            botMessage.classList.add('bot-message');
            // Check if botReply contains HTML (e.g., starts with '<table>')
            if (botReply.startsWith('<table')) {
                botMessage.innerHTML = botReply; // Use innerHTML for HTML content
            } else {
                displayWritingAnimation(botReply, botMessage); // Use text animation for plain text
            }
            chatBox.appendChild(botMessage);
        });

        input.value = "";
    }
}

function displayWritingAnimation(message, element) {
    // If message is HTML, append it directly without animation
    if (message.startsWith('<table')) {
        element.innerHTML = message;
    } else {
        // Else, use typing animation for text
        let index = 0;
        const intervalId = setInterval(() => {
            if (index < message.length) {
                element.textContent += message[index];
                index++;
            } else {
                clearInterval(intervalId);
            }
        }, 10); // Speed of writing animation, adjust as needed
    }
}
