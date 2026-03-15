// ==============================
// CONFIG
// ==============================
const BASE_URL = "http://127.0.0.1:8000";

// ==============================
// Globals
// ==============================
let documentId = null;

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
// Greeting
// ==============================
function setGreeting() {
  const h = new Date().getHours();
  const g = document.getElementById("greetingMsg");

  if (!g) return;

  g.innerText =
    h < 12 ? "🌞 Good Morning!" :
    h < 18 ? "☀️ Good Afternoon!" :
    "🌙 Good Evening!";
}

// ==============================
// Recents
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
      `<p style="color: gray; font-size: 14px;">No recent documents</p>`;
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
// Backend Check
// ==============================
async function checkBackend() {

  try {

    const res = await fetch(`${BASE_URL}/ping`);

    if (!res.ok) throw new Error();

    console.log("✅ Backend connected");

    return true;

  } catch {

    console.error("❌ Backend not reachable");

    return false;
  }
}

// ==============================
// Upload Document
// ==============================
const fileInput = document.getElementById("fileInput");

if (fileInput) {

  fileInput.addEventListener("change", async (e) => {

    const file = e.target.files[0];

    if (!file) return;

    document.getElementById("fileDetails").innerText =
      `📄 ${file.name} (${formatFileSize(file.size)})`;

    saveToRecents(file.name, formatFileSize(file.size));

    const backendAlive = await checkBackend();

    if (!backendAlive) {
      alert("Backend not running on port 8000");
      return;
    }

    try {

      const formData = new FormData();

      formData.append("file", file);

      const res = await fetch(`${BASE_URL}/upload`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();

      documentId = data.document_id;

      console.log("✅ Upload successful. Document ID:", documentId);

    } catch (err) {

      console.error("Upload error:", err);

      alert("Upload failed. Check backend.");

    }

  });

}

// ==============================
// Ask Question
// ==============================
const submitBtn = document.getElementById("submitBtn");

if (submitBtn) {

  submitBtn.addEventListener("click", async () => {

    const questionInput = document.getElementById("questionInput");

    const responseBox = document.getElementById("responseBox");

    const messageBox = document.getElementById("messageBox");

    const question = questionInput.value.trim();

    if (!documentId) {

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

      const res = await fetch(`${BASE_URL}/ask`, {

        method: "POST",

        headers: { "Content-Type": "application/json" },

        body: JSON.stringify({
          document_id: documentId,
          question: question
        })

      });

      if (!res.ok) throw new Error();

      const data = await res.json();

      responseBox.innerText = data.answer;

    } catch (err) {

      console.error(err);

      responseBox.innerText = "❌ Backend error";

    }

  });

}

// ==============================
// Theme Toggle
// ==============================
const themeToggle = document.getElementById("themeToggle");

if (themeToggle) {

  themeToggle.addEventListener("change", (e) => {

    document.body.classList.toggle("dark-mode", e.target.checked);

  });

}

// ==============================
// On Load
// ==============================
window.addEventListener("DOMContentLoaded", async () => {

  setGreeting();

  renderRecents();

  await checkBackend();

});