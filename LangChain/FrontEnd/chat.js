/**
 * Chatbot flotante para sitios web.
 * 
 * Este script crea un botón flotante en la esquina inferior derecha que,
 * al hacer clic, muestra una interfaz de chat simple. El chatbot se comunica
 * con un backend mediante peticiones `POST` para enviar y recibir mensajes.
 *
 * Variables globales configurables (se deben definir antes de cargar el script):
 * @global {string} window.BOT_NAME - Nombre del bot (por defecto: "Agustin").
 * @global {string} window.BACKEND_URL - URL del backend que recibe las consultas (por defecto: "http://localhost:8000/chat").
 * @global {string} window.BOT_SALUDO - Mensaje de saludo inicial (por defecto: mensaje con nombre del bot).
 *
 * Funcionalidades:
 * - Botón flotante con ícono 💬.
 * - Contenedor de chat con encabezado, historial de mensajes y campo de entrada.
 * - Comunicación con el backend mediante `fetch` (método POST).
 * - Autorespuesta de bienvenida y continuidad de conversación usando `id_conversacion`.
 *
 * Requiere:
 * - El backend debe aceptar y devolver JSON con los campos:
 *   - input: texto del usuario.
 *   - id_conversacion: identificador opcional para continuar una conversación.
 *   - respuesta: texto de respuesta del bot.
 */

(() => {
  // Configuración global
  const BOT_NAME = window.BOT_NAME || "Agustin";
  const BACKEND_URL = window.BACKEND_URL || "http://localhost:8000/chat";
  const SALUDO_INICIAL =
    window.BOT_SALUDO ||
    `Hola soy un asistente automatizado, me llamo ${BOT_NAME}, ¿en qué te puedo ayudar?`;

  // Botón flotante del chat
  const boton = document.createElement("div");
  boton.innerText = "💬";
  // Estilos del botón
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

  // Contenedor principal del chat
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

  // Área donde aparecen los mensajes del chat
  const chatArea = document.createElement("div");
  chatArea.id = "chatbox-messages";
  chatArea.style = `
    flex: 1;
    padding: 10px;
    overflow-y: auto;
    font-family: sans-serif;
    font-size: 14px;
  `;

  // Contenedor para el input de texto y botón de envío
  const inputContainer = document.createElement("div");
  inputContainer.style = `
    display: flex;
    align-items: center;
    padding: 8px;
    border-top: 1px solid #ccc;
    background: #f9f9f9;
    gap: 8px;
  `;

  // Input de texto del usuario
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

  // Botón de enviar
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

  // Efectos hover
  enviarBtn.onmouseover = () => enviarBtn.style.background = "#098c8b";
  enviarBtn.onmouseout = () => enviarBtn.style.background = "#0ABFAD";

  // Armado de DOM
  inputContainer.appendChild(input);
  inputContainer.appendChild(enviarBtn);
  chatBox.appendChild(chatHeader);
  chatBox.appendChild(chatArea);
  chatBox.appendChild(inputContainer);
  document.body.appendChild(boton);
  document.body.appendChild(chatBox);

  /**
   * Agrega un mensaje al área del chat.
   * 
   * @param {string} text - Texto del mensaje.
   * @param {"user"|"bot"} from - Origen del mensaje (por defecto: "bot").
   */
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

    bubble.style.borderBottomRightRadius = from === "user" ? "4px" : "18px";
    bubble.style.borderBottomLeftRadius = from === "bot" ? "4px" : "18px";

    wrapper.appendChild(bubble);
    chatArea.appendChild(wrapper);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  /** @type {string|null} idConversacion - ID de sesión del backend para mantener el hilo del chat */
  let idConversacion = null;

  /**
   * Envía un mensaje al backend y muestra la respuesta.
   * 
   * @param {string} text - Mensaje del usuario.
   */
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

  /** @type {boolean} chatIniciado - Controla si se ejecutó el saludo inicial */
  let chatIniciado = false;

  // Evento de clic en el botón flotante
  boton.onclick = async () => {
    if (chatBox.style.display === "none") {
      chatBox.style.display = "flex";

      if (!chatIniciado) {
        chatIniciado = true;
        appendMessage("...", "bot");

        try {
          const res = await fetch(BACKEND_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: "", id_conversacion: idConversacion }),
          });
          const data = await res.json();
          idConversacion = data.id_conversacion;
          chatArea.lastChild.textContent = "";
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

  // Envío al hacer clic en "Enviar"
  enviarBtn.onclick = () => {
    const texto = input.value.trim();
    if (texto !== "") sendMessage(texto);
  };

  // Envío con tecla Enter
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") enviarBtn.click();
  });

  // Saludo inicial al cargar la página
  window.addEventListener("DOMContentLoaded", () => {
    chatBox.style.display = "flex";
    appendMessage(SALUDO_INICIAL, "bot");
  });
})();
