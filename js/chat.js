/* Real-time chat UI — Поміч поруч */
window.PP = window.PP || {};

PP.resolveMediaUrl = PP.resolveMediaUrl || ((url) => {
  if (!url) return "";
  if (/^https?:\/\//i.test(url)) return url;
  const base = PP.API_BASE.replace(/\/api\/v1\/?$/, "");
  return url.startsWith("/") ? `${base}${url}` : `${base}/${url}`;
});

PP.resolveWsBase = () => PP.API_BASE.replace(/\/api\/v1\/?$/, "").replace(/^http/i, "ws");

PP._escapeHtml = (str) => {
  const d = document.createElement("div");
  d.textContent = str || "";
  return d.innerHTML;
};

PP._formatChatTime = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const now = new Date();
  const sameDay =
    d.getDate() === now.getDate() &&
    d.getMonth() === now.getMonth() &&
    d.getFullYear() === now.getFullYear();
  const opts = sameDay
    ? { hour: "2-digit", minute: "2-digit" }
    : { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" };
  return d.toLocaleString("uk-UA", opts);
};

PP._chatUserId = () => {
  if (PP._chatState?.viewerId != null) return PP._chatState.viewerId;
  try {
    const u = JSON.parse(localStorage.getItem("pp-user") || "null");
    if (u?.id != null) return Number(u.id);
  } catch {
    /* ignore */
  }
  const token = PP._token?.();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
    const raw = payload.user_id ?? payload.sub;
    if (raw != null && String(raw).match(/^\d+$/)) return Number(raw);
  } catch {
    /* ignore */
  }
  return null;
};

PP._normalizeChatMessage = (m) => {
  const msg = { ...m };
  const uid = PP._chatUserId();
  if (uid != null && msg.sender_id != null) {
    msg.is_own = Number(msg.sender_id) === uid;
  } else if (uid != null && msg.is_own == null) {
    msg.is_own = false;
  } else {
    msg.is_own = !!msg.is_own;
  }
  return msg;
};

PP._renderChatAttachment = (m) => {
  if (!m.attachment) return "";
  const url = PP.resolveMediaUrl(m.attachment);
  const name = PP._escapeHtml(m.attachment_name || "Файл");
  if (m.attachment_type === "photo") {
    return `<a class="chat-attach-photo" href="${url}" target="_blank" rel="noopener">
      <img src="${url}" alt="${name}" loading="lazy" decoding="async">
    </a>`;
  }
  return `<a class="chat-attach-doc" href="${url}" target="_blank" rel="noopener" download>
    <span class="chat-attach-doc-icon" aria-hidden="true">📄</span>
    <span class="chat-attach-doc-name">${name}</span>
  </a>`;
};

PP._renderChatMessage = (m) => {
  const msg = PP._normalizeChatMessage(m);
  const text = msg.text ? `<p class="chat-msg-text">${PP._escapeHtml(msg.text)}</p>` : "";
  const attach = PP._renderChatAttachment(msg);
  const time = PP._formatChatTime(msg.created_at);
  const readMark = msg.is_own && msg.is_read ? '<span class="chat-msg-read" aria-label="Прочитано">✓✓</span>' : "";
  const pending = String(msg.id).startsWith("pending-") ? " pending" : "";
  return `<div class="chat-msg ${msg.is_own ? "own" : "other"}${pending}" data-id="${msg.id}">
    ${text}${attach}
    <div class="chat-msg-meta"><time datetime="${msg.created_at || ""}">${time}</time>${readMark}</div>
  </div>`;
};

PP._removeChatMessage = (msgsEl, id) => {
  msgsEl.querySelector(`.chat-msg[data-id="${id}"]`)?.remove();
  PP._chatState.knownIds.delete(id);
};

PP._upsertChatMessage = (msgsEl, m) => {
  const msg = PP._normalizeChatMessage(m);
  const existing = msgsEl.querySelector(`.chat-msg[data-id="${msg.id}"]`);
  if (existing) {
    existing.outerHTML = PP._renderChatMessage(msg);
    PP._chatState.knownIds.add(msg.id);
    msgsEl.scrollTop = msgsEl.scrollHeight;
    return;
  }
  if (PP._chatState.knownIds.has(msg.id)) return;
  PP._chatState.knownIds.add(msg.id);
  msgsEl.insertAdjacentHTML("beforeend", PP._renderChatMessage(msg));
  msgsEl.scrollTop = msgsEl.scrollHeight;
};

PP._renderChatMessages = (msgsEl, messages) => {
  PP._chatState.knownIds = new Set();
  const list = messages.results || messages;
  PP._chatState.hasMore = !!messages.has_more;
  msgsEl.innerHTML = list.map((m) => {
    PP._chatState.knownIds.add(m.id);
    return PP._renderChatMessage(m);
  }).join("");
  msgsEl.scrollTop = msgsEl.scrollHeight;
};

PP._prependChatMessages = (msgsEl, messages) => {
  const list = messages.results || messages;
  PP._chatState.hasMore = !!messages.has_more;
  if (!list.length) return;
  const prevHeight = msgsEl.scrollHeight;
  const html = list
    .filter((m) => !PP._chatState.knownIds.has(m.id))
    .map((m) => {
      PP._chatState.knownIds.add(m.id);
      return PP._renderChatMessage(m);
    })
    .join("");
  msgsEl.insertAdjacentHTML("afterbegin", html);
  msgsEl.scrollTop = msgsEl.scrollHeight - prevHeight;
};

PP._revokeChatPreviewUrl = () => {
  if (PP._chatState.previewObjectUrl) {
    URL.revokeObjectURL(PP._chatState.previewObjectUrl);
    PP._chatState.previewObjectUrl = null;
  }
};

PP._bindChatVisualViewport = (wrapEl) => {
  if (!wrapEl || !window.visualViewport) return () => {};
  const sync = () => {
    const vv = window.visualViewport;
    const offset = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
    wrapEl.style.setProperty("--chat-keyboard-offset", `${offset}px`);
  };
  visualViewport.addEventListener("resize", sync);
  visualViewport.addEventListener("scroll", sync);
  sync();
  return () => {
    visualViewport.removeEventListener("resize", sync);
    visualViewport.removeEventListener("scroll", sync);
  };
};

PP._validateChatFile = (file) => {
  if (!file) return null;
  const max = 20 * 1024 * 1024;
  if (file.size > max) return "Файл завеликий (макс. 20 МБ).";
  const okTypes = /^(image\/(jpeg|png|webp|gif|heic|heif)|application\/(pdf|msword|vnd\.openxmlformats-officedocument\.wordprocessingml\.document))$/i;
  const name = (file.name || "").toLowerCase();
  const okExt = /\.(jpe?g|png|webp|gif|heic|heif|pdf|docx?)$/;
  if (!okTypes.test(file.type || "") && !okExt.test(name)) {
    return "Недозволений тип файлу.";
  }
  return null;
};

PP.initChatPage = async (role) => {
  const listEl = document.querySelector(".chat-list");
  const msgsEl = document.getElementById("chat-messages");
  const form = document.getElementById("chat-form");
  const headerEl = document.querySelector(".chat-header");
  const layoutEl = document.querySelector(".chat-layout");
  const wrapEl = document.querySelector(".cabinet-chat-wrap");
  if (!listEl || !msgsEl || !form) return;

  document.body.classList.add("pp-chat-page");
  document.documentElement.classList.add("pp-chat-page");
  PP._ensureChatListToolbar(layoutEl, role);
  PP._bindChatVisualViewport(wrapEl);

  const syncChatBreakpoint = () => {
    if (!PP._isMobileChat()) {
      layoutEl?.classList.remove("chat-mode-list", "chat-mode-thread");
      document.body.classList.remove("pp-chat-list", "pp-chat-thread");
      return;
    }
    if (layoutEl.classList.contains("chat-mode-thread") || layoutEl.classList.contains("chat-mode-list")) {
      PP._setChatMobileMode(
        layoutEl,
        layoutEl.classList.contains("chat-mode-thread") ? "thread" : "list"
      );
      return;
    }
    PP._setChatMobileMode(layoutEl, PP._chatState?.activeId ? "thread" : "list");
  };

  if (PP._isMobileChat()) PP._setChatMobileMode(layoutEl, "list");
  else {
    layoutEl?.classList.remove("chat-mode-list", "chat-mode-thread");
    document.body.classList.remove("pp-chat-list", "pp-chat-thread");
  }
  window.addEventListener("resize", syncChatBreakpoint, { passive: true });

  try {
    const me = await PP.fetchMe();
    if (me?.id != null) {
      PP._chatState.viewerId = Number(me.id);
      PP.saveSession({
        user: me,
        tokens: { access: PP._token(), refresh: localStorage.getItem("pp-refresh-token") },
      });
    }
  } catch {
    PP._chatState.viewerId = PP._chatUserId();
  }

  const fileInput = form.querySelector('input[type="file"]') || (() => {
    const fi = document.createElement("input");
    fi.type = "file";
    fi.hidden = true;
    fi.accept = "image/*,.pdf,.doc,.docx";
    form.appendChild(fi);
    return fi;
  })();

  let previewEl = form.querySelector(".chat-file-preview");
  if (!previewEl) {
    previewEl = document.createElement("div");
    previewEl.className = "chat-file-preview";
    previewEl.hidden = true;
    form.insertBefore(previewEl, form.firstChild);
  }

  const clearPreview = () => {
    PP._revokeChatPreviewUrl();
    fileInput.value = "";
    previewEl.hidden = true;
    previewEl.innerHTML = "";
  };

  form.querySelector(".chat-attach")?.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    const file = fileInput.files?.[0];
    PP._revokeChatPreviewUrl();
    if (!file) {
      clearPreview();
      return;
    }
    const err = PP._validateChatFile(file);
    if (err) {
      PP.showToast?.(err, "error");
      clearPreview();
      return;
    }
    previewEl.hidden = false;
    const isImg = file.type.startsWith("image/");
    const objUrl = isImg ? URL.createObjectURL(file) : "";
    if (objUrl) PP._chatState.previewObjectUrl = objUrl;
    previewEl.innerHTML = isImg
      ? `<img src="${objUrl}" alt="" class="chat-file-thumb"><span>${PP._escapeHtml(file.name)}</span><button type="button" class="chat-file-clear" aria-label="Прибрати">×</button>`
      : `<span class="chat-attach-doc-icon">📄</span><span>${PP._escapeHtml(file.name)}</span><button type="button" class="chat-file-clear" aria-label="Прибрати">×</button>`;
    previewEl.querySelector(".chat-file-clear")?.addEventListener("click", clearPreview);
  });

  const showList = () => {
    if (PP._isMobileChat()) PP._setChatMobileMode(layoutEl, "list");
  };
  const showThread = () => {
    if (PP._isMobileChat()) PP._setChatMobileMode(layoutEl, "thread");
  };

  const refreshList = async (activeId) => {
    const convs = await PP.fetchConversations();
    const list = convs.results || convs;
    PP._renderChatList(listEl, list, role, activeId);
    return list;
  };

  const loadOlder = async () => {
    const id = PP._chatState.activeId;
    if (!id || !PP._chatState.hasMore || PP._chatState.loadingOlder) return;
    const first = msgsEl.querySelector(".chat-msg:not([data-id^='pending-'])");
    const beforeId = first ? Number(first.dataset.id) : null;
    if (!beforeId) return;
    PP._chatState.loadingOlder = true;
    try {
      const msgs = await PP.fetchMessages(id, { beforeId });
      if (PP._chatState.activeId !== id) return;
      PP._prependChatMessages(msgsEl, msgs);
    } catch {
      /* ignore */
    } finally {
      PP._chatState.loadingOlder = false;
    }
  };

  msgsEl.addEventListener("scroll", () => {
    if (msgsEl.scrollTop < 48) loadOlder();
  });

  const selectConversation = async (id, convs) => {
    PP._chatState.activeId = id;
    showThread();
    const conv = convs.find((c) => Number(c.id) === Number(id));
    if (headerEl && conv) {
      PP._renderChatHeader(headerEl, conv, role, showList);
    }
    listEl.querySelectorAll(".chat-list-item").forEach((b) => {
      b.classList.toggle("active", Number(b.dataset.id) === Number(id));
    });
    const msgs = await PP.fetchMessages(id);
    if (PP._chatState.activeId !== id) return;
    PP._renderChatMessages(msgsEl, msgs);
    if (PP._chatState.activeId !== id) return;
    PP._connectChatRealtime(id, msgsEl, () => {
      if (PP._chatState.activeId === id) refreshList(id);
    });
    await refreshList(id);
  };

  const matchNannyConv = (list, nannyId) =>
    list.find((c) => Number(c.nanny) === nannyId || Number(c.nanny?.id) === nannyId);

  try {
    let convs = await PP.fetchConversations();
    convs = convs.results || convs;
    const nannyParam = new URLSearchParams(location.search).get("nanny");
    let activeId = null;

    if ((role === "parent" || role === "admin") && nannyParam) {
      const nannyId = Number(nannyParam);
      let conv = matchNannyConv(convs, nannyId);
      if (!conv) {
        try {
          conv = await PP.startConversation(nannyId);
          convs = [conv, ...convs.filter((c) => Number(c.id) !== Number(conv.id))];
        } catch (err) {
          PP.showToast?.(err.message || "Не вдалося відкрити чат", "error");
          throw err;
        }
      }
      activeId = conv.id;
    }

    const visible = PP._filterChatList(convs, activeId);
    if (!visible.length && !activeId) {
      listEl.innerHTML = '<p class="chat-empty">Немає розмов</p>';
      return;
    }

    const isMobile = PP._isMobileChat();
    const openThreadNow = Boolean(activeId) || !isMobile;
    if (!activeId && !isMobile) activeId = visible[0]?.id || null;

    PP._renderChatList(listEl, convs, role, openThreadNow ? activeId : null);
    if (activeId && openThreadNow) {
      await selectConversation(activeId, convs);
    } else {
      showList();
    }

    listEl.addEventListener("click", async (e) => {
      const btn = e.target.closest(".chat-list-item");
      if (!btn) return;
      const id = Number(btn.dataset.id);
      const fresh = await refreshList(id);
      await selectConversation(id, fresh);
    });
  } catch (e) {
    console.warn(e);
    listEl.innerHTML = '<p class="chat-empty">Немає розмов / помилка завантаження</p>';
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = PP._chatState.activeId;
    if (!id) return;
    const input = form.querySelector('input[type="text"], input:not([type="file"]):not([hidden])');
    const text = input?.value?.trim();
    const file = fileInput.files?.[0];
    if (!text && !file) return;
    const fileErr = PP._validateChatFile(file);
    if (fileErr) {
      PP.showToast?.(fileErr, "error");
      return;
    }
    const submitBtn = form.querySelector('[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    const uid = PP._chatUserId();
    const pendingId = `pending-${Date.now()}`;
    const now = new Date().toISOString();
    PP._chatState.pendingSend = true;

    PP._upsertChatMessage(msgsEl, {
      id: pendingId,
      text: text || "",
      sender_id: uid,
      is_own: true,
      created_at: now,
      attachment: file && file.type.startsWith("image/") ? PP._chatState.previewObjectUrl : null,
      attachment_type: file ? (file.type.startsWith("image/") ? "photo" : "document") : "",
      attachment_name: file?.name || "",
    });
    if (input) input.value = "";

    try {
      const msg = await PP.sendMessage(id, text, file);
      clearPreview();
      PP._removeChatMessage(msgsEl, pendingId);
      PP._upsertChatMessage(msgsEl, msg);
      await refreshList(id);
    } catch (err) {
      PP._removeChatMessage(msgsEl, pendingId);
      if (input && text) input.value = text;
      PP.showToast?.(err.message || "Не вдалося надіслати", "error");
    } finally {
      PP._chatState.pendingSend = false;
      if (submitBtn) submitBtn.disabled = false;
    }
  });

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && PP._chatState.activeId) {
      const id = PP._chatState.activeId;
      PP.fetchMessages(id).then((msgs) => {
        if (PP._chatState.activeId === id) PP._renderChatMessages(msgsEl, msgs);
      }).catch(() => {});
      refreshList(id).catch(() => {});
    }
  });
};
