/* ============================================================
   GlobalInfo Chatbot — Frontend Logic
   ============================================================ */

const API_BASE = 'http://127.0.0.1:8000';

// DOM refs
const messagesContainer = document.getElementById('messages-container');
const welcomeCard       = document.getElementById('welcome-card');
const userInput         = document.getElementById('user-input');
const sendBtn           = document.getElementById('send-btn');
const typingWrapper     = document.getElementById('typing-wrapper');
const clearBtn          = document.getElementById('clear-btn');
const chipList          = document.getElementById('chip-list');
const sidebar           = document.getElementById('sidebar');
const sidebarToggle     = document.getElementById('sidebar-toggle');
const mobileMenuBtn     = document.getElementById('mobile-menu-btn');

// State
let isWaitingForResponse = false;

// ============================================================
// Sidebar toggle (desktop)
// ============================================================
sidebarToggle.addEventListener('click', () => {
  sidebar.classList.toggle('collapsed');
  sidebarToggle.querySelector('.toggle-icon').textContent =
    sidebar.classList.contains('collapsed') ? '›' : '‹';
});

// ============================================================
// Mobile sidebar overlay
// ============================================================
const overlay = document.createElement('div');
overlay.className = 'sidebar-overlay';
document.body.appendChild(overlay);

mobileMenuBtn.addEventListener('click', () => {
  sidebar.classList.add('mobile-open');
  overlay.classList.add('visible');
});

overlay.addEventListener('click', closeMobileSidebar);

function closeMobileSidebar() {
  sidebar.classList.remove('mobile-open');
  overlay.classList.remove('visible');
}

// ============================================================
// Quick-query chips
// ============================================================
chipList.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const query = chip.dataset.query;
    fillAndSend(query);
    closeMobileSidebar();
  });
});

// Welcome card example tags
welcomeCard.querySelectorAll('.example-tag').forEach(tag => {
  tag.addEventListener('click', () => {
    const query = tag.dataset.query;
    fillAndSend(query);
  });
});

function fillAndSend(text) {
  userInput.value = text;
  autoResize();
  updateSendBtn();
  sendMessage();
}

// ============================================================
// Input handling
// ============================================================
userInput.addEventListener('input', () => {
  autoResize();
  updateSendBtn();
});

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) sendMessage();
  }
});

sendBtn.addEventListener('click', sendMessage);

function autoResize() {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

function updateSendBtn() {
  sendBtn.disabled = userInput.value.trim() === '' || isWaitingForResponse;
}

// ============================================================
// Clear chat
// ============================================================
clearBtn.addEventListener('click', () => {
  // Remove all message rows (not the welcome card)
  const rows = messagesContainer.querySelectorAll('.message-row, .timestamp-line');
  rows.forEach(r => r.remove());

  // Restore welcome card
  welcomeCard.style.display = 'flex';
  welcomeCard.style.flexDirection = 'column';
});

// ============================================================
// Send message
// ============================================================
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || isWaitingForResponse) return;

  // Hide welcome card on first message
  welcomeCard.style.display = 'none';

  // Append user bubble
  appendMessage('user', text);

  // Clear input
  userInput.value = '';
  autoResize();
  updateSendBtn();

  // Show typing indicator
  showTyping(true);
  isWaitingForResponse = true;
  updateSendBtn();

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    showTyping(false);
    appendMessage('bot', data.response);

  } catch (err) {
    showTyping(false);
    const errMsg = err.message.includes('Failed to fetch')
      ? '⚠️ Cannot connect to the backend. Please make sure the FastAPI server is running:\n\n`uvicorn main:app --reload`'
      : `⚠️ ${err.message}`;
    appendMessage('bot', errMsg, true);
  } finally {
    isWaitingForResponse = false;
    updateSendBtn();
  }
}

// ============================================================
// Append message bubble
// ============================================================
function appendMessage(role, rawText, isError = false) {
  const row = document.createElement('div');
  row.className = `message-row ${role === 'user' ? 'user-row' : ''}`;

  // Avatar
  const avatar = document.createElement('div');
  avatar.className = `avatar ${role === 'bot' ? 'bot-avatar' : 'user-avatar'}`;
  avatar.textContent = role === 'bot' ? '🌍' : '👤';

  // Bubble
  const bubble = document.createElement('div');
  bubble.className = `bubble ${role === 'bot' ? 'bot-bubble' : 'user-bubble'} ${isError ? 'error-bubble' : ''}`;
  bubble.innerHTML = parseMarkdown(rawText);

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesContainer.appendChild(row);

  // Timestamp
  const ts = document.createElement('p');
  ts.className = 'timestamp';
  ts.textContent = formatTime(new Date());
  messagesContainer.appendChild(ts);

  // Scroll to bottom
  scrollToBottom();
}

// ============================================================
// Minimal Markdown-like parser
// ============================================================
function parseMarkdown(text) {
  // Escape HTML first
  let html = escapeHtml(text);

  // Code blocks (backtick): `code`
  html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(56,189,248,0.1);padding:1px 5px;border-radius:4px;font-size:0.85em;">$1</code>');

  // Bold: **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Italic: *text*
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Links: [text](url)
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Line breaks
  html = html.replace(/\n/g, '<br>');

  return html;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ============================================================
// Typing indicator
// ============================================================
function showTyping(visible) {
  typingWrapper.classList.toggle('visible', visible);
  if (visible) scrollToBottom();
}

// ============================================================
// Helpers
// ============================================================
function scrollToBottom() {
  requestAnimationFrame(() => {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  });
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ============================================================
// Init — send a greeting from the bot after a short delay
// ============================================================
window.addEventListener('DOMContentLoaded', () => {
  // Focus input when ready
  userInput.focus();
});
