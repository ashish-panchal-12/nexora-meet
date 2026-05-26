/**
 * NexMeet — Room JS
 * Handles Jitsi Meet embed + WebSocket chat
 */

let chatSocket = null;
let unreadCount = 0;
let chatOpen = true;

function initRoom(meetingId, username, meetingTitle, wsUrl) {
  initJitsi(meetingId, username, meetingTitle);
  initChat(wsUrl, username);
  handleResize();
  window.addEventListener('resize', handleResize);
}

/* ─── JITSI ─── */
function initJitsi(meetingId, username, meetingTitle) {
  const domain = 'meet.jit.si';
  const options = {
    roomName: 'nexmeet_' + meetingId,
    width: '100%',
    height: '100%',
    parentNode: document.querySelector('#jitsi-container'),
    userInfo: { displayName: username },
    configOverwrite: {
      startWithAudioMuted: false,
      startWithVideoMuted: false,
      disableDeepLinking: true,
      prejoinPageEnabled: false,
    },
    interfaceConfigOverwrite: {
      TOOLBAR_BUTTONS: [
        'microphone', 'camera', 'closedcaptions', 'desktop',
        'fullscreen', 'fodeviceselection', 'hangup', 'chat',
        'recording', 'livestreaming', 'sharedvideo', 'settings',
        'raisehand', 'videoquality', 'filmstrip', 'invite',
        'tileview', 'select-background', 'mute-everyone',
      ],
      SHOW_JITSI_WATERMARK: false,
      SHOW_BRAND_WATERMARK: false,
      DEFAULT_BACKGROUND: '#0d0d14',
      filmStripOnly: false,
    },
  };
  const api = new JitsiMeetExternalAPI(domain, options);
  api.addEventListener('readyToClose', () => {
    window.location.href = '/meetings/dashboard/';
  });
  window._jitsiApi = api;
}

/* ─── WEBSOCKET CHAT ─── */
function initChat(wsUrl, username) {
  chatSocket = new WebSocket(wsUrl);

  chatSocket.onopen = () => {
    console.log('Chat connected');
  };

  chatSocket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === 'chat') {
      appendMessage(data.username, data.message, data.timestamp, data.username === username);
    } else if (data.type === 'system') {
      appendSystem(data.message);
    }
    if (!chatOpen) {
      unreadCount++;
      const badge = document.getElementById('unreadBadge');
      badge.textContent = unreadCount;
      badge.style.display = 'flex';
    }
  };

  chatSocket.onclose = () => {
    appendSystem('Connection lost. Please refresh.');
  };

  chatSocket.onerror = () => {
    appendSystem('Chat connection error.');
  };

  window._username = username;
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg || !chatSocket || chatSocket.readyState !== WebSocket.OPEN) return;
  chatSocket.send(JSON.stringify({ message: msg, username: window._username }));
  input.value = '';
  input.focus();
}

function appendMessage(username, message, timestamp, isSelf) {
  const box = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `chat-msg ${isSelf ? 'chat-msg-self' : 'chat-msg-other'}`;
  div.innerHTML = `
    <div class="chat-msg-meta">
      <span class="chat-msg-user">${isSelf ? 'You' : escapeHtml(username)}</span>
      <span class="chat-msg-time">${timestamp || ''}</span>
    </div>
    <div class="chat-msg-bubble">${escapeHtml(message)}</div>
  `;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function appendSystem(text) {
  const box = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-system';
  div.textContent = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

/* ─── CHAT TOGGLE ─── */
function toggleChat() {
  const sidebar = document.getElementById('chatSidebar');
  const floatBtn = document.getElementById('floatChatBtn');
  chatOpen = !chatOpen;
  sidebar.style.display = chatOpen ? 'flex' : 'none';
  floatBtn.style.display = chatOpen ? 'none' : 'flex';
  if (chatOpen) {
    unreadCount = 0;
    const badge = document.getElementById('unreadBadge');
    if (badge) badge.style.display = 'none';
  }
}

function handleResize() {
  if (window.innerWidth < 768) {
    chatOpen = false;
    const sidebar = document.getElementById('chatSidebar');
    const floatBtn = document.getElementById('floatChatBtn');
    if (sidebar) sidebar.style.display = 'none';
    if (floatBtn) floatBtn.style.display = 'flex';
  } else {
    chatOpen = true;
    const sidebar = document.getElementById('chatSidebar');
    const floatBtn = document.getElementById('floatChatBtn');
    if (sidebar) sidebar.style.display = 'flex';
    if (floatBtn) floatBtn.style.display = 'none';
  }
}

/* ─── COPY MEETING ID ─── */
function copyMeetingId() {
  const id = document.querySelector('.room-id-bar') ? 
    document.querySelector('.room-id-bar').textContent.trim() : '';
  navigator.clipboard.writeText(id).then(() => {
    const btn = document.getElementById('copyIdBtn');
    btn.innerHTML = '<i class="bi bi-check-lg"></i> Copied!';
    setTimeout(() => btn.innerHTML = '<i class="bi bi-copy"></i> Copy ID', 2000);
  });
}
