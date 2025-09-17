const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('input');
const formEl = document.getElementById('composer');
const sendBtn = document.getElementById('send');
const themeToggle = document.getElementById('themeToggle');
const tpl = document.getElementById('bubble');

// --- Theme ---
(function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  if (saved === 'light') document.body.classList.add('light');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light');
      localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
    });
  }
})();

// --- State ---
let history = JSON.parse(localStorage.getItem('chat-history') || '[]');
renderHistory();

function renderHistory() {
  if (!chatEl) return;
  chatEl.innerHTML = '';
  history.forEach(m => addMessage(m.role, m.text, m.time));
  scrollToBottom();
}

function addMessage(role, text, time) {
  const node = tpl.content.cloneNode(true);
  const msg = node.querySelector('.msg');
  if (role === 'me') msg.classList.add('me');
  msg.querySelector('.text').textContent = text;
  msg.querySelector('.time').textContent = time || new Date().toLocaleTimeString();
  chatEl.appendChild(node);
}

function addTyping() {
  const node = tpl.content.cloneNode(true);
  const msg = node.querySelector('.msg');
  msg.classList.remove('me');
  const bubble = node.querySelector('.bubble');
  bubble.querySelector('.text').innerHTML = `<span class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>`;
  bubble.querySelector('.meta .time').textContent = '…';
  chatEl.appendChild(node);
  return bubble; // return bubble to replace later
}

function scrollToBottom() { if (chatEl) chatEl.scrollTop = chatEl.scrollHeight; }

// --- Autosize textarea ---
function autosize() {
  if (!inputEl) return;
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(180, inputEl.scrollHeight) + 'px';
}
if (inputEl) inputEl.addEventListener('input', autosize);
autosize();

// --- Submit ---
if (formEl) formEl.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;

  // Optimistic UI for user
  const myTime = new Date().toLocaleTimeString();
  addMessage('me', text, myTime);
  history.push({ role: 'me', text, time: myTime });
  localStorage.setItem('chat-history', JSON.stringify(history));
  inputEl.value = '';
  autosize();
  sendBtn.disabled = true;

  const typingBubble = addTyping();
  scrollToBottom();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();

    // Replace typing with actual reply
    typingBubble.querySelector('.text').textContent = data.reply;
    typingBubble.parentElement.querySelector('.time').textContent = new Date().toLocaleTimeString();

    history.push({ role: 'bot', text: data.reply, time: new Date().toLocaleTimeString() });
    localStorage.setItem('chat-history', JSON.stringify(history));
  } catch (err) {
    typingBubble.querySelector('.text').textContent = 'Network error. Please try again.';
  } finally {
    sendBtn.disabled = false;
    scrollToBottom();
  }
});

// --- Keyboard behavior ---
if (inputEl) inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    formEl.requestSubmit();
  }
});
