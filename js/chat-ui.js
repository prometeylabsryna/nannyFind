/* Chat UI helpers — Поміч поруч */
window.PP = window.PP || {};

PP._renderChatHeader = (headerEl, conv, role, onBack) => {
  if (!headerEl || !conv) return;
  const isNannyView = role === "nanny";
  const name = isNannyView ? conv.parent_name : conv.nanny_name;
  const roleLabel = isNannyView
    ? (conv.conversation_type === "admin" ? "Підтримка" : "Батько")
    : "Няня";
  const displayName = (name || "").trim() || "Співрозмовник";
  const initial = displayName.charAt(0).toUpperCase();
  const back = onBack
    ? `<button type="button" class="chat-back" aria-label="До списку чатів">←</button>`
    : "";
  headerEl.innerHTML = `${back}<div class="chat-header-inner">
    <span class="chat-header-avatar" aria-hidden="true">${PP._escapeHtml(initial)}</span>
    <div class="chat-header-info">
      <span class="chat-header-name">${PP._escapeHtml(displayName)}</span>
      <span class="chat-header-role">${roleLabel}</span>
    </div>
  </div>`;
  headerEl.querySelector(".chat-back")?.addEventListener("click", onBack);
};

PP._filterChatList = (convs, activeId) =>
  (convs || []).filter((c) => {
    if (Number(c.id) === Number(activeId)) return true;
    const count = c.messages_count;
    if (count != null) return Number(count) > 0;
    return !!c.last_message;
  });

PP._chatHomeHref = (role) => {
  if (role === "nanny") return PP.ROUTES.nannyCabinet;
  if (role === "admin") return PP.ROUTES.admin;
  return PP.ROUTES.parentCabinet;
};

PP._ensureChatListToolbar = (layoutEl, role) => {
  let panel = layoutEl?.querySelector(".chat-list-panel");
  const listEl = layoutEl?.querySelector(".chat-list");
  if (!layoutEl || !listEl) return;
  if (!panel) {
    panel = document.createElement("div");
    panel.className = "chat-list-panel";
    listEl.parentNode.insertBefore(panel, listEl);
    panel.appendChild(listEl);
  }
  let toolbar = panel.querySelector(".chat-list-toolbar");
  if (!toolbar) {
    toolbar = document.createElement("div");
    toolbar.className = "chat-list-toolbar";
    toolbar.innerHTML = `
      <a class="chat-nav-home" href="${PP._chatHomeHref(role)}" aria-label="До кабінету">←</a>
      <h1 class="chat-list-title">Повідомлення</h1>`;
    panel.insertBefore(toolbar, listEl);
  } else {
    const home = toolbar.querySelector(".chat-nav-home");
    if (home) home.setAttribute("href", PP._chatHomeHref(role));
  }
};

PP._renderChatList = (listEl, convs, role, activeId) => {
  const visible = PP._filterChatList(convs, activeId);
  if (!visible.length) {
    listEl.innerHTML = '<p class="chat-empty">Поки немає розмов.<br>Напишіть няні з її профілю — діалог зʼявиться тут.</p>';
    return;
  }
  listEl.innerHTML = visible
    .map((c) => {
      const name = (role === "nanny" ? c.parent_name : c.nanny_name) || "Співрозмовник";
      const initial = name.trim().charAt(0).toUpperCase() || "?";
      const preview = c.last_message?.text || (c.last_message?.attachment ? "📎 Файл" : "Немає повідомлень");
      const time = PP._formatChatTime(c.last_message?.created_at || c.updated_at);
      const unreadCount =
        Number(c.id) === Number(activeId) ? 0 : Number(c.unread_count || 0);
      const unread = unreadCount > 0 ? `<span class="chat-unread">${unreadCount}</span>` : "";
      return `<button type="button" class="chat-list-item${Number(c.id) === Number(activeId) ? " active" : ""}" data-id="${c.id}">
        <span class="chat-list-avatar" aria-hidden="true">${PP._escapeHtml(initial)}</span>
        <span class="chat-list-body">
          <span class="chat-list-top">
            <span class="chat-list-name">${PP._escapeHtml(name)}</span>
            <span class="chat-list-time">${time}</span>
          </span>
          <span class="chat-list-bottom">
            <span class="chat-list-preview">${PP._escapeHtml(preview)}</span>
            ${unread}
          </span>
        </span>
      </button>`;
    })
    .join("");
};

PP._isMobileChat = () => window.matchMedia("(max-width: 767px)").matches;

PP._setChatMobileMode = (layoutEl, mode) => {
  if (!layoutEl) return;
  layoutEl.classList.toggle("chat-mode-list", mode === "list");
  layoutEl.classList.toggle("chat-mode-thread", mode === "thread");
  document.body.classList.toggle("pp-chat-list", mode === "list");
  document.body.classList.toggle("pp-chat-thread", mode === "thread");
};
