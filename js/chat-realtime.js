/* Chat realtime — WebSocket + polling fallback */
window.PP = window.PP || {};

PP._chatState = PP._chatState || {
  socket: null,
  pollTimer: null,
  listPollTimer: null,
  lastSeenMsgId: new Map(),
  reconnectTimer: null,
  reconnectAttempt: 0,
  activeId: null,
  knownIds: new Set(),
  viewerId: null,
  pendingSend: false,
  hasMore: false,
  loadingOlder: false,
  previewObjectUrl: null,
};

PP._clearChatReconnect = () => {
  if (PP._chatState.reconnectTimer) {
    clearTimeout(PP._chatState.reconnectTimer);
    PP._chatState.reconnectTimer = null;
  }
};

PP._stopChatPolling = () => {
  if (PP._chatState.pollTimer) {
    clearInterval(PP._chatState.pollTimer);
    PP._chatState.pollTimer = null;
  }
};

PP._disconnectChatRealtime = () => {
  PP._clearChatReconnect();
  PP._stopChatPolling();
  const ws = PP._chatState.socket;
  PP._chatState.socket = null;
  if (ws) {
    ws.onclose = null;
    ws.onerror = null;
    ws.onmessage = null;
    try {
      ws.close();
    } catch {
      /* ignore */
    }
  }
  PP._chatState.reconnectAttempt = 0;
};

PP._startChatPolling = (convId, msgsEl, onRemoteActivity) => {
  if (PP._chatState.pollTimer) return;
  PP._chatState.pollTimer = setInterval(async () => {
    if (PP._chatState.activeId !== convId) return;
    try {
      const msgs = await PP.fetchMessages(convId);
      const list = msgs.results || msgs;
      const last = list[list.length - 1];
      if (last && !PP._chatState.knownIds.has(last.id)) {
        PP._renderChatMessages(msgsEl, msgs);
        onRemoteActivity?.();
      }
    } catch {
      /* ignore transient errors */
    }
  }, 4000);
};

PP._scheduleChatReconnect = (convId, msgsEl, onRemoteActivity) => {
  if (PP._chatState.activeId !== convId) return;
  PP._clearChatReconnect();
  const attempt = PP._chatState.reconnectAttempt || 0;
  if (attempt >= 5) {
    PP._startChatPolling(convId, msgsEl, onRemoteActivity);
    return;
  }
  const delay = Math.min(30000, 1000 * 2 ** attempt);
  PP._chatState.reconnectAttempt = attempt + 1;
  PP._chatState.reconnectTimer = setTimeout(() => {
    if (PP._chatState.activeId === convId) {
      PP._connectChatRealtime(convId, msgsEl, onRemoteActivity, true);
    }
  }, delay);
};

PP._handleChatSocketPayload = (payload, convId, msgsEl, onRemoteActivity) => {
  if (payload.type === "auth_ok") return;
  if (payload.type === "message" && payload.data) {
    const data = payload.data;
    const uid = PP._chatUserId();
    if (PP._chatState.pendingSend && uid != null && Number(data.sender_id) === uid) {
      return;
    }
    PP._upsertChatMessage(msgsEl, data);
    if (uid != null && Number(data.sender_id) !== uid) {
      PP.markChatRead?.(convId)?.then(() => onRemoteActivity?.()).catch(() => onRemoteActivity?.());
    } else {
      onRemoteActivity?.();
    }
  }
  if (payload.type === "read" && payload.data?.message_ids) {
    payload.data.message_ids.forEach((id) => {
      const el = msgsEl.querySelector(`.chat-msg[data-id="${id}"] .chat-msg-read`);
      if (!el) {
        const msg = msgsEl.querySelector(`.chat-msg.own[data-id="${id}"] .chat-msg-meta`);
        if (msg) {
          msg.insertAdjacentHTML(
            "beforeend",
            '<span class="chat-msg-read" aria-label="Прочитано">✓✓</span>'
          );
        }
      }
    });
    onRemoteActivity?.();
  }
};

PP._connectChatRealtime = (convId, msgsEl, onRemoteActivity, isReconnect = false) => {
  if (!isReconnect) {
    PP._disconnectChatRealtime();
  } else {
    PP._clearChatReconnect();
    const old = PP._chatState.socket;
    PP._chatState.socket = null;
    if (old) {
      old.onclose = null;
      try {
        old.close();
      } catch {
        /* ignore */
      }
    }
  }

  const token = PP._token?.();
  if (!token) {
    PP._startChatPolling(convId, msgsEl, onRemoteActivity);
    return;
  }

  const wsUrl = `${PP.resolveWsBase()}/ws/chat/${convId}/`;
  let ws;
  try {
    ws = new WebSocket(wsUrl);
  } catch {
    PP._scheduleChatReconnect(convId, msgsEl, onRemoteActivity);
    return;
  }

  PP._chatState.socket = ws;
  let opened = false;

  ws.onopen = () => {
    opened = true;
    PP._stopChatPolling();
    PP._chatState.reconnectAttempt = 0;
    try {
      ws.send(JSON.stringify({ type: "auth", token }));
    } catch {
      ws.close();
    }
  };

  ws.onmessage = (ev) => {
    let payload;
    try {
      payload = JSON.parse(ev.data);
    } catch {
      return;
    }
    PP._handleChatSocketPayload(payload, convId, msgsEl, onRemoteActivity);
  };

  ws.onclose = () => {
    if (PP._chatState.socket === ws) PP._chatState.socket = null;
    if (PP._chatState.activeId === convId) {
      PP._scheduleChatReconnect(convId, msgsEl, onRemoteActivity);
    }
  };

  ws.onerror = () => {
    if (!opened) ws.close();
  };
};
