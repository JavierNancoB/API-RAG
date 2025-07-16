(() => {
  // Configuración global básica (puedes sobreescribir estas variables antes de cargar el script)
  const BOT_NAME = window.BOT_NAME || "Agustin";
  const BACKEND_URL = window.BACKEND_URL || "http://localhost:8000/chat";
  const SALUDO_INICIAL =
    window.BOT_SALUDO ||
    `Hola soy un asistente automatizado, me llamo ${BOT_NAME}, ¿en qué te puedo ayudar?`;

  // Crear botón flotante
  const boton = document.createElement("div");
  boton.innerText = "💬";
    boton.style = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    background: #0ABFAD;
    color: white;
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: pointer;
    z-index: 9999;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    `;

    // Cabecera del chat
  const chatHeader = document.createElement("div");
  chatHeader.textContent = "🤖 Asistente Alloxentric";
  chatHeader.style = `
    background: white;
    border-bottom: 2px solid #0ABFAD;
   color: #0ABFAD;
    font-weight: bold;
    text-align: center;
    padding: 10px;
    font-family: sans-serif;
    font-size: 14px;
  `;



  // Crear contenedor del chat
  const chatBox = document.createElement("div");
  chatBox.style = `
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 300px;
    height: 400px;
    background: white;
    border: 1px solid #ccc;
    border-radius: 12px;
    display: none;
    flex-direction: column;
    z-index: 9999;
    box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    overflow: hidden;
  `;

  const chatArea = document.createElement("div");
  chatArea.style = "flex: 1; padding: 10px; overflow-y: auto; font-family: sans-serif; font-size: 14px;";
  chatArea.id = "chatbox-messages";

  const inputContainer = document.createElement("div");
    inputContainer.style = `
    display: flex;
    align-items: center;
    padding: 8px;
    border-top: 1px solid #ccc;
    background: #f9f9f9;
    gap: 8px;
  `;


  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Escribe aquí...";
  input.style = `
    flex: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 20px;
    font-size: 14px;
    outline: none;
  `;


  const enviarBtn = document.createElement("button");
  enviarBtn.textContent = "Enviar";
  enviarBtn.style = `
    padding: 10px 16px;
    background: #0ABFAD;
    color: white;
    border: none;
    border-radius: 20px;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.3s;
 `;

  enviarBtn.onmouseover = () => {
    enviarBtn.style.background = "#098c8b";
  };
  enviarBtn.onmouseout = () => {
    enviarBtn.style.background = "#0ABFAD";
  };

  inputContainer.appendChild(input);
  inputContainer.appendChild(enviarBtn);

  chatBox.appendChild(chatHeader);
  chatBox.appendChild(chatArea);
  chatBox.appendChild(inputContainer);

  document.body.appendChild(boton);
  document.body.appendChild(chatBox);

  // Función para mostrar mensajes
    function appendMessage(text, from = "bot") {
    const wrapper = document.createElement("div");
    wrapper.style = `
        display: flex;
        justify-content: ${from === "user" ? "flex-end" : "flex-start"};
        margin-bottom: 8px;
    `;

    const bubble = document.createElement("div");
    bubble.textContent = text;
    bubble.style = `
        background: ${from === "user" ? "#DCF8C6" : "#E8E8E8"};
        color: #222;
        padding: 10px 14px;
        max-width: 80%;
        font-size: 14px;
        border-radius: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        white-space: pre-wrap;
        word-wrap: break-word;
    `;

    if (from === "user") {
        bubble.style.borderBottomRightRadius = "4px";
    } else {
        bubble.style.borderBottomLeftRadius = "4px";
    }

    wrapper.appendChild(bubble);
    chatArea.appendChild(wrapper);
    chatArea.scrollTop = chatArea.scrollHeight;
    }


  // Enviar mensaje al backend
  let idConversacion = null;
  async function sendMessage(text) {
    appendMessage(text, "user");
    input.value = "";

    const res = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        input: text,
        id_conversacion: idConversacion,
      }),
    }).then((r) => r.json());

    idConversacion = res.id_conversacion;
    appendMessage(res.respuesta, "bot");
  }

  // Listeners
  let chatIniciado = false;

  boton.onclick = async () => {
  if (chatBox.style.display === "none") {
      chatBox.style.display = "flex";

      if (!chatIniciado) {
      chatIniciado = true;
      appendMessage("...", "bot"); // mensaje provisional

      try {
          const res = await fetch(BACKEND_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input: "", id_conversacion: idConversacion }),
          });
          const data = await res.json();
          idConversacion = data.id_conversacion;
          chatArea.lastChild.textContent = ""; // quita "..."
          appendMessage(data.respuesta, "bot");
      } catch (error) {
          chatArea.lastChild.textContent = "Error al conectar con el servidor.";
          console.error(error);
      }
      }
  } else {
      chatBox.style.display = "none";
  }
  };

  enviarBtn.onclick = () => {
    const texto = input.value.trim();
    if (texto !== "") {
      sendMessage(texto);
    }
  };

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") enviarBtn.click();
  });

  // Mostrar saludo inicial
  window.addEventListener("DOMContentLoaded", () => {
    chatBox.style.display = "flex";
    appendMessage(SALUDO_INICIAL, "bot");
  });
})();
