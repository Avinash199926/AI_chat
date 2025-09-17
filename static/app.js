// const chatEl = document.getElementById('chat');
// const inputEl = document.getElementById('input');
// const formEl = document.getElementById('composer');
// const sendBtn = document.getElementById('send');
// const themeToggle = document.getElementById('themeToggle');
// const tpl = document.getElementById('bubble');

// // --- Theme ---
// (function initTheme() {
//   const saved = localStorage.getItem('theme') || 'dark';
//   if (saved === 'light') document.body.classList.add('light');
//   if (themeToggle) {
//     themeToggle.addEventListener('click', () => {
//       document.body.classList.toggle('light');
//       localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
//     });
//   }
// })();

// // --- State ---
// let history = JSON.parse(localStorage.getItem('chat-history') || '[]');
// renderHistory();

// function renderHistory() {
//   if (!chatEl) return;
//   chatEl.innerHTML = '';
//   history.forEach(m => addMessage(m.role, m.text, m.time));
//   scrollToBottom();
// }

// function addMessage(role, text, time) {
//   const node = tpl.content.cloneNode(true);
//   const msg = node.querySelector('.msg');
//   if (role === 'me') msg.classList.add('me');
//   msg.querySelector('.text').textContent = text;
//   msg.querySelector('.time').textContent = time || new Date().toLocaleTimeString();
//   chatEl.appendChild(node);
// }

// function addTyping() {
//   const node = tpl.content.cloneNode(true);
//   const msg = node.querySelector('.msg');
//   msg.classList.remove('me');
//   const bubble = node.querySelector('.bubble');
//   bubble.querySelector('.text').innerHTML = `<span class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>`;
//   bubble.querySelector('.meta .time').textContent = '…';
//   chatEl.appendChild(node);
//   return bubble; // return bubble to replace later
// }

// function scrollToBottom() { if (chatEl) chatEl.scrollTop = chatEl.scrollHeight; }

// // --- Autosize textarea ---
// function autosize() {
//   if (!inputEl) return;
//   inputEl.style.height = 'auto';
//   inputEl.style.height = Math.min(180, inputEl.scrollHeight) + 'px';
// }
// if (inputEl) inputEl.addEventListener('input', autosize);
// autosize();

// // --- Submit ---
// if (formEl) formEl.addEventListener('submit', async (e) => {
//   e.preventDefault();
//   const text = inputEl.value.trim();
//   if (!text) return;

//   // Optimistic UI for user
//   const myTime = new Date().toLocaleTimeString();
//   addMessage('me', text, myTime);
//   history.push({ role: 'me', text, time: myTime });
//   localStorage.setItem('chat-history', JSON.stringify(history));
//   inputEl.value = '';
//   autosize();
//   sendBtn.disabled = true;

//   const typingBubble = addTyping();
//   scrollToBottom();

//   try {
//     const res = await fetch('/api/chat', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ message: text })
//     });
//     const data = await res.json();

//     // Replace typing with actual reply
//     typingBubble.querySelector('.text').textContent = data.reply;
//     typingBubble.parentElement.querySelector('.time').textContent = new Date().toLocaleTimeString();

//     history.push({ role: 'bot', text: data.reply, time: new Date().toLocaleTimeString() });
//     localStorage.setItem('chat-history', JSON.stringify(history));
//   } catch (err) {
//     typingBubble.querySelector('.text').textContent = 'Network error. Please try again.';
//   } finally {
//     sendBtn.disabled = false;
//     scrollToBottom();
//   }
// });

// // --- Keyboard behavior ---
// if (inputEl) inputEl.addEventListener('keydown', (e) => {
//   if (e.key === 'Enter' && !e.shiftKey) {
//     e.preventDefault();
//     formEl.requestSubmit();
//   }
// });



// const chatEl = document.getElementById('chat');
// const inputEl = document.getElementById('input');
// const formEl = document.getElementById('composer');
// const sendBtn = document.getElementById('send');
// const themeToggle = document.getElementById('themeToggle');
// const tpl = document.getElementById('bubble');

// // --- Theme ---
// (function initTheme() {
//   const saved = localStorage.getItem('theme') || 'dark';
//   if (saved === 'light') document.body.classList.add('light');
//   if (themeToggle) {
//     themeToggle.addEventListener('click', () => {
//       document.body.classList.toggle('light');
//       localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
//     });
//   }
// })();

// // --- State ---
// let history = JSON.parse(localStorage.getItem('chat-history') || '[]');
// renderHistory();

// function renderHistory() {
//   if (!chatEl) return;
//   chatEl.innerHTML = '';
//   history.forEach(m => addMessage(m.role, m.text, m.time));
//   scrollToBottom();
// }

// function addMessage(role, text, time) {
//   const node = tpl.content.cloneNode(true);
//   const msg = node.querySelector('.msg');
//   if (role === 'me') msg.classList.add('me');
//   msg.querySelector('.text').textContent = text;
//   msg.querySelector('.time').textContent = time || new Date().toLocaleTimeString();
//   chatEl.appendChild(node);
// }

// function addTyping() {
//   const node = tpl.content.cloneNode(true);
//   const msg = node.querySelector('.msg');
//   msg.classList.remove('me');
//   const bubble = node.querySelector('.bubble');
//   bubble.querySelector('.text').innerHTML = `<span class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>`;
//   bubble.querySelector('.meta .time').textContent = '…';
//   chatEl.appendChild(node);
//   return bubble; // return bubble to replace later
// }

// function scrollToBottom() { if (chatEl) chatEl.scrollTop = chatEl.scrollHeight; }

// // --- Autosize textarea ---
// function autosize() {
//   if (!inputEl) return;
//   inputEl.style.height = 'auto';
//   inputEl.style.height = Math.min(180, inputEl.scrollHeight) + 'px';
// }
// if (inputEl) inputEl.addEventListener('input', autosize);
// autosize();

// // --- Submit ---
// if (formEl) formEl.addEventListener('submit', async (e) => {
//   e.preventDefault();
//   const text = inputEl.value.trim();
//   if (!text) return;

//   // Optimistic UI for user
//   const myTime = new Date().toLocaleTimeString();
//   addMessage('me', text, myTime);
//   history.push({ role: 'me', text, time: myTime });
//   localStorage.setItem('chat-history', JSON.stringify(history));
//   inputEl.value = '';
//   autosize();
//   sendBtn.disabled = true;

//   const typingBubble = addTyping();
//   scrollToBottom();

//   try {
//     const res = await fetch('/api/chat', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ message: text })
//     });
//     const data = await res.json();

//     // Replace typing with actual reply
//     typingBubble.querySelector('.text').textContent = data.reply;
//     typingBubble.parentElement.querySelector('.time').textContent = new Date().toLocaleTimeString();

//     history.push({ role: 'bot', text: data.reply, time: new Date().toLocaleTimeString() });
//     localStorage.setItem('chat-history', JSON.stringify(history));
//   } catch (err) {
//     typingBubble.querySelector('.text').textContent = 'Network error. Please try again.';
//   } finally {
//     sendBtn.disabled = false;
//     scrollToBottom();
//   }
// });

// // --- Keyboard behavior ---
// if (inputEl) inputEl.addEventListener('keydown', (e) => {
//   if (e.key === 'Enter' && !e.shiftKey) {
//     e.preventDefault();
//     formEl.requestSubmit();
//   }
// });


// /static/app.js

const chatEl = document.getElementById('chat');
const formEl = document.getElementById('composer');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');
const themeToggle = document.getElementById('themeToggle');

const chatListEl = document.getElementById('chatList');
const newChatBtn = document.getElementById('newChat');
const renameChatBtn = document.getElementById('renameChat');
const deleteChatBtn = document.getElementById('deleteChat');

const bubbleTpl = document.getElementById('bubble');
const chatItemTpl = document.getElementById('chatItem');

let currentChatId = localStorage.getItem('currentChatId') || null;
let chatsCache = []; // [{chat_id,title,...}]

// ---------- Helpers ----------
function makeBubble(role, text, ts) {
  const node = bubbleTpl.content.firstElementChild.cloneNode(true);
  node.classList.toggle('from-user', role === 'user');
  node.classList.toggle('from-bot', role !== 'user');
  node.querySelector('.avatar').textContent = role === 'user' ? '🧑' : '🤖';
  node.querySelector('.text').textContent = text || '';
  node.querySelector('.time').textContent = ts ? new Date(ts).toLocaleString() : new Date().toLocaleString();
  return node;
}

function appendBubble(role, text, ts) {
  const b = makeBubble(role, text, ts);
  chatEl.appendChild(b);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function clearChatView() {
  chatEl.innerHTML = '';
}

function setActiveChat(id) {
  currentChatId = id;
  localStorage.setItem('currentChatId', id || '');
  // highlight
  [...chatListEl.children].forEach(li => li.classList.remove('active'));
  const active = [...chatListEl.children].find(li => li.dataset.id === id);
  if (active) active.classList.add('active');
}

function renderChatList(list) {
  chatListEl.innerHTML = '';
  list.forEach(c => {
    const node = chatItemTpl.content.firstElementChild.cloneNode(true);
    node.querySelector('.chat-title').textContent = c.title || 'New chat';
    node.dataset.id = c.chat_id;
    node.addEventListener('click', () => openChat(c.chat_id));
    chatListEl.appendChild(node);
  });
  // keep active highlight
  if (currentChatId) setActiveChat(currentChatId);
}

async function fetchJSON(url, opts = {}) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ---------- API ----------
async function listChats() {
  const data = await fetchJSON('/api/chats');
  chatsCache = data.chats || [];
  renderChatList(chatsCache);
  // if no current chat, select the newest one automatically
  if (!currentChatId && chatsCache.length) {
    await openChat(chatsCache[0].chat_id);
  } else if (currentChatId) {
    // ensure it exists
    const exists = chatsCache.some(c => c.chat_id === currentChatId);
    if (!exists && chatsCache.length) {
      await openChat(chatsCache[0].chat_id);
    } else if (exists) {
      await openChat(currentChatId);
    }
  }
}

async function createChat(initialTitle = 'New chat') {
  const data = await fetchJSON('/api/chats', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: initialTitle})
  });
  // refresh list and open it
  await listChats();
  await openChat(data.chat_id);
}

async function openChat(chatId) {
  clearChatView();
  setActiveChat(chatId);
  const data = await fetchJSON(`/api/chats/${chatId}`);
  (data.messages || []).forEach(m => appendBubble(m.role, m.text, m.ts));
}

async function renameChat() {
  if (!currentChatId) return;
  const currentTitle = (chatsCache.find(c => c.chat_id === currentChatId) || {}).title || '';
  const title = prompt('Rename chat to:', currentTitle);
  if (!title) return;
  await fetchJSON(`/api/chats/${currentChatId}`, {
    method: 'PATCH',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title})
  });
  await listChats();
}

async function deleteChat() {
  if (!currentChatId) return;
  if (!confirm('Delete this chat and all its messages?')) return;
  await fetchJSON(`/api/chats/${currentChatId}`, { method: 'DELETE' });
  currentChatId = null;
  localStorage.removeItem('currentChatId');
  await listChats();
  clearChatView();
}

// ---------- Messaging ----------
async function sendMessage(text) {
  // append optimistic user bubble
  appendBubble('user', text);

  // typing placeholder
  const typing = makeBubble('assistant', '…');
  typing.classList.add('typing');
  chatEl.appendChild(typing);
  chatEl.scrollTop = chatEl.scrollHeight;

  try {
    const data = await fetchJSON('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, chat_id: currentChatId})
    });
    currentChatId = data.chat_id; // API ensures it
    localStorage.setItem('currentChatId', currentChatId);

    // replace typing with reply
    typing.querySelector('.text').textContent = data.reply || '[no reply]';
    typing.querySelector('.time').textContent = new Date().toLocaleString();
    typing.classList.remove('typing');

    // refresh chat list (title may have changed from first message)
    await listChats();
    setActiveChat(currentChatId);
  } catch (e) {
    typing.querySelector('.text').textContent = '[error sending message]';
  }
}

// ---------- UI events ----------
const autoresize = () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 220) + 'px';
};

formEl.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = (inputEl.value || '').trim();
  if (!text) return;
  inputEl.value = '';
  autoresize();
  sendMessage(text);
});

inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    formEl.requestSubmit();
  }
});
inputEl.addEventListener('input', autoresize);

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
  });
  if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.classList.add('dark');
  }
}

newChatBtn.addEventListener('click', () => createChat('New chat'));
renameChatBtn.addEventListener('click', renameChat);
deleteChatBtn.addEventListener('click', deleteChat);

// ---------- Init ----------
(async function init() {
  autoresize();
  await listChats();
})();

