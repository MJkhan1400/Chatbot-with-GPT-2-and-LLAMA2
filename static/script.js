const chatBox = document.querySelector(".chat-box");
const messageInput = document.querySelector("#message-input");
const sendBtn = document.querySelector("#send-btn");
const loader = document.querySelector(".loader");
const gpt2Btn = document.querySelector("#gpt2-btn");
const llama2Btn = document.querySelector("#llama2-btn");

// Initially set GPT-2 as active model
let activeModel = "gpt2";

document.addEventListener("DOMContentLoaded", function() {
  toggleActiveModel(activeModel);
});

function toggleActiveModel(model) {
  activeModel = model; // Update the active model

  if (model === "gpt2") {
    gpt2Btn.classList.add("active");
    llama2Btn.classList.remove("active");
  } else {
    llama2Btn.classList.add("active");
    gpt2Btn.classList.remove("active");
  }
}

// Function to add message to chat box
function addMessage(message, isUserMessage) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("mt-3", "p-3", "rounded");

  if (isUserMessage) {
    messageDiv.classList.add("user-message");
  } else {
    messageDiv.classList.add("bot-message");
  }

  messageDiv.innerHTML = `
    <img src="/static/images/user.png" class="user-icon"><p>${message}</p>
  `;

  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to handle sending message
function sendMessage() {
  const message = messageInput.value.trim();

  if (message !== "") {
    addMessage(message, true);
    loader.style.display = "block"; // Show loader before sending request

    fetch("/api", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message, model: activeModel }) // Send active model along with message
    })
    .then(response => response.json())
    .then(data => {
      messageInput.value = "";
      loader.style.display = "none"; // Hide loader after receiving response

      const botLogo = activeModel === "gpt2" ? "/static/images/gpt-2.png" : "/static/images/llama.png"; // Choose logo based on model

      const messageDiv = document.createElement("div");
      messageDiv.classList.add("mt-3", "p-3", "rounded", "bot-message");

      const content = data.response;

      messageDiv.innerHTML = `
        <img src="${botLogo}" class="bot-icon"><p>${content}</p>
      `;

      chatBox.appendChild(messageDiv);
      chatBox.scrollTop = chatBox.scrollHeight;

    })
    .catch(error => console.error(error));
  }
}

// Event listeners for buttons
sendBtn.addEventListener("click", sendMessage);
messageInput.addEventListener("keydown", event => {
  if (event.keyCode === 13 && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

gpt2Btn.addEventListener("click", () => {
  activeModel = "gpt2";
  toggleActiveModel("gpt2");
});

llama2Btn.addEventListener("click", () => {
  activeModel = "llama2";
  toggleActiveModel("llama2");
});
