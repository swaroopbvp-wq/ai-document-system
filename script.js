// ==============================
// Utility
// ==============================
function formatFileSize(bytes) {
  const kb = bytes / 1024;
  return kb > 1024
    ? (kb / 1024).toFixed(2) + " MB"
    : kb.toFixed(2) + " KB";
}

// ==============================
// Globals
// ==============================
let documentText = "";

// ==============================
// Greeting
// ==============================
function setGreeting() {
  const h = new Date().getHours();
  const g = document.getElementById("greetingMsg");

  g.innerText =
    h < 12 ? "🌞 Good Morning!" :
    h < 18 ? "☀️ Good Afternoon!" :
    "🌙 Good Evening!";
}

// ==============================
// Recents (optional, safe)
// ==============================
function saveToRecents(fileName, fileSize) {
  let recents = JSON.parse(localStorage.getItem("recents")) || [];
  recents.unshift({ name: fileName, size: fileSize });
  recents = recents.slice(0, 5);
  localStorage.setItem("recents", JSON.stringify(recents));
  renderRecents();
}

function renderRecents() {
  const recentsList = document.getElementById("recentsList");
  if (!recentsList) return;

  const recents = JSON.parse(localStorage.getItem("recents")) || [];
  if (!recents.length) {
    recentsList.innerHTML =
      `<p style="color: gray; font-size: 14px; padding: 8px;">No recent documents</p>`;
    return;
  }

  recentsList.innerHTML = "";
  recents.forEach(f => {
    const div = document.createElement("div");
    div.innerText = `📄 ${f.name} (${f.size})`;
    recentsList.appendChild(div);
  });
}

// ==============================
// File Upload
// ==============================
document.getElementById("fileInput").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  document.getElementById("fileDetails").innerText =
    `📄 ${file.name} (${formatFileSize(file.size)})`;

  saveToRecents(file.name, formatFileSize(file.size));

  const reader = new FileReader();
  reader.onload = () => {
    documentText = reader.result;
  };
  reader.readAsText(file);
});

// ==============================
// SUBMIT → REAL BACKEND CALL
// ==============================
document.getElementById("submitBtn").addEventListener("click", async () => {
  const question = document.getElementById("questionInput").value.trim();
  const responseBox = document.getElementById("responseBox");
  const messageBox = document.getElementById("messageBox");

  // Validation
  if (!documentText) {
    messageBox.style.display = "block";
    messageBox.innerText = "Please upload a document first.";
    return;
  }

  if (!question) {
    messageBox.style.display = "block";
    messageBox.innerText = "Please enter a question.";
    return;
  }

  messageBox.style.display = "none";
  responseBox.innerText = "⏳ Processing...";

  try {
    const res = await fetch("http://127.0.0.1:8001/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document: documentText,
        question: question
      })
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();

    // ✅ THIS IS THE FIX
    responseBox.innerText = data.answer;

  } catch (err) {
    console.error(err);
    responseBox.innerText = "❌ Backend not reachable";
  }
});

// ==============================
// Chatbot UI (dummy)
// ==============================
document.getElementById("chatbotToggle").addEventListener("click", () => {
  const panel = document.getElementById("chatbotPanel");
  panel.style.display = panel.style.display === "flex" ? "none" : "flex";
});

document.getElementById("chatbotSend").addEventListener("click", () => {
  const q = document.getElementById("chatbotQuery").value.trim();
  if (!q) return;
  document.getElementById("responseBox").innerText = "🤖 " + q;
  document.getElementById("chatbotQuery").value = "";
});

// ==============================
// Settings
// ==============================
document.getElementById("settingsBtn").addEventListener("click", () => {
  const panel = document.getElementById("settingsPanel");
  panel.style.display = panel.style.display === "block" ? "none" : "block";
});

document.getElementById("themeToggle").addEventListener("change", (e) => {
  document.body.classList.toggle("dark-mode", e.target.checked);
  document.getElementById("themeLabel").innerText =
    e.target.checked ? "🌙 Dark Mode" : "🌞 Light Mode";
});

// ==============================
// On Load
// ==============================
window.addEventListener("DOMContentLoaded", () => {
  setGreeting();
  renderRecents();
});