// Função que verifica se a tecla pressionada foi o Enter
function verificarEnter(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function sendMessage() {
    var userInputElement = document.getElementById("userInput");
    var userText = userInputElement.value.trim();

    // Evita enviar mensagens em branco
    if (userText === "") return;

    var chatbox = document.getElementById("chatbox");

    // Adiciona a mensagem do usuário na tela
    chatbox.innerHTML += "<div class='message user-msg'>" + userText + "</div>";
    
    // Limpa o campo de texto imediatamente
    userInputElement.value = "";
    
    // Rola a tela para o final
    chatbox.scrollTop = chatbox.scrollHeight;

    // Envia para o backend Flask
    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText })
    })
    .then(response => response.json())
    .then(data => {
        // Adiciona a resposta do Gemini na tela
        chatbox.innerHTML += "<div class='message bot-msg'>" + data.response + "</div>";
        // Rola a tela para baixo novamente
        chatbox.scrollTop = chatbox.scrollHeight;
    })
    .catch(error => {
        console.error("Erro:", error);
    });
}