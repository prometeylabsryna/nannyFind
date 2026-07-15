/* Cabinet shared: auth guard, nav, helpers */
window.PP = window.PP || {};

PP.requireAuth = async (roles = []) => {
  const sessionOk = await PP.waitForSession();
  const token = PP._token();
  if (!sessionOk || !token) {
    location.href = `${PP.ROUTES.login}?next=${encodeURIComponent(location.pathname + location.search)}`;
    return false;
  }

  try {
    const user = await PP.fetchMe();
    PP.saveSession({
      user,
      tokens: {
        access: PP._token(),
        refresh: localStorage.getItem("pp-refresh-token"),
      },
    });

    if (user.status === "blocked") {
      PP.clearSession();
      alert("Акаунт заблоковано.");
      location.href = PP.ROUTES.login;
      return false;
    }

    const hasRequiredRole = roles.length === 0
      || roles.includes(user.role)
      || (roles.includes("admin") && PP.isPlatformAdmin(user));

    if (!hasRequiredRole) {
      const next = encodeURIComponent(location.pathname + location.search);
      if (roles.includes("parent") && user.role === "nanny") {
        alert("Щоб написати няні, потрібен акаунт батьків.");
        location.replace(`${PP.ROUTES.login}?next=${next}&reauth=1`);
      } else if (roles.includes("admin")) {
        alert("Доступ лише для адміністраторів.");
        location.replace(`${PP.ROUTES.login}?next=${next}&reauth=1`);
      } else {
        location.replace(PP.authHomeForRole(user.role, user));
      }
      return false;
    }

    PP.updateAuthHeader?.();
    return true;
  } catch (err) {
    if (err.status === 401) {
      PP.clearSession();
      location.href = `${PP.ROUTES.login}?next=${encodeURIComponent(location.pathname + location.search)}`;
      return false;
    }
    alert(err.message || "Немає з'єднання з сервером. Спробуйте ще раз.");
    return false;
  }
};

PP.initCabinetDrawer = (title = "Кабінет") => {
  const layout = document.querySelector(".cabinet-layout, .admin-layout");
  const sidebar = document.querySelector(".cabinet-sidebar");
  if (!layout || !sidebar) return;

  sidebar.id = "cabinet-drawer";
  sidebar.setAttribute("role", "dialog");
  sidebar.setAttribute("aria-modal", "true");
  sidebar.setAttribute("aria-label", title);
  if (!sidebar.classList.contains("is-open")) sidebar.setAttribute("aria-hidden", "true");

  let backdrop = document.getElementById("cabinet-drawer-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "cabinet-drawer-backdrop";
    backdrop.className = "cabinet-drawer-backdrop";
    backdrop.hidden = true;
    document.body.appendChild(backdrop);
  }

  if (!sidebar.querySelector(".cabinet-drawer-head")) {
    const head = document.createElement("div");
    head.className = "cabinet-drawer-head";
    head.innerHTML = `<span class="cabinet-drawer-title">${title}</span><button type="button" class="cabinet-drawer-close" aria-label="Закрити меню">×</button>`;
    sidebar.insertBefore(head, sidebar.firstChild);
  } else {
    const t = sidebar.querySelector(".cabinet-drawer-title");
    if (t) t.textContent = title;
  }

  if (sidebar.dataset.drawerReady) return;
  sidebar.dataset.drawerReady = "1";

  const contentEl = layout.querySelector(".cabinet-main")
    || [...layout.children].find((el) =>
      !el.classList.contains("cabinet-sidebar")
      && !el.classList.contains("cabinet-mobile-nav")
      && !el.classList.contains("cabinet-chat-wrap")
      && !el.classList.contains("admin-main")
    );
  const mobileNav = layout.querySelector(".cabinet-mobile-nav");

  let toggle = document.getElementById("cabinet-nav-toggle");
  if (!toggle) {
    toggle = document.createElement("button");
    toggle.type = "button";
    toggle.id = "cabinet-nav-toggle";
    toggle.className = "btn btn-secondary cabinet-nav-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", "cabinet-drawer");
    toggle.innerHTML = '<span class="cabinet-nav-toggle-icon" aria-hidden="true"><span></span><span></span><span></span></span>Меню';
    if (contentEl) contentEl.insertBefore(toggle, contentEl.firstChild);
    else if (mobileNav) mobileNav.appendChild(toggle);
    else layout.insertBefore(toggle, sidebar.nextSibling);
  }

  const closeBtn = sidebar.querySelector(".cabinet-drawer-close");
  let lastFocus = null;

  const close = () => {
    sidebar.classList.remove("is-open");
    sidebar.setAttribute("aria-hidden", "true");
    backdrop.classList.remove("is-visible");
    backdrop.hidden = true;
    document.body.classList.remove("cabinet-drawer-open");
    toggle.setAttribute("aria-expanded", "false");
    if (lastFocus) lastFocus.focus();
  };

  const open = () => {
    lastFocus = document.activeElement;
    sidebar.classList.add("is-open");
    sidebar.setAttribute("aria-hidden", "false");
    backdrop.hidden = false;
    requestAnimationFrame(() => backdrop.classList.add("is-visible"));
    document.body.classList.add("cabinet-drawer-open");
    toggle.setAttribute("aria-expanded", "true");
    closeBtn?.focus();
  };

  toggle.addEventListener("click", () => {
    if (sidebar.classList.contains("is-open")) close();
    else open();
  });
  closeBtn?.addEventListener("click", close);
  backdrop.addEventListener("click", close);
  sidebar.addEventListener("click", (e) => {
    if (e.target.closest(".cabinet-nav-link")) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sidebar.classList.contains("is-open")) close();
  });
};

PP.initCabinetNav = (nav, activePath) => {
  const navEl = document.getElementById("parent-nav") || document.getElementById("nanny-nav") || document.getElementById("admin-nav");
  const path = activePath || location.pathname;
  const drawerTitle = path.includes("/parent/") ? "Кабінет батьків"
    : path.includes("/nanny/") ? "Кабінет няні"
    : PP.isAdminPath(path) ? "Адмін-панель" : "Кабінет";
  if (navEl && nav) navEl.innerHTML = PP.renderCabinetNav(nav, path);
  if (document.getElementById("admin-nav") && nav === PP.ADMIN_NAV) {
    document.getElementById("admin-nav").innerHTML =
      '<div class="admin-label">Адмін</div>' + PP.renderCabinetNav(PP.ADMIN_NAV, path);
  }
  PP.initCabinetDrawer(drawerTitle);
};

PP.docStatusBadge = (status) => {
  const map = {
    pending: '<span class="badge badge-trust">Очікує</span>',
    approved: '<span class="badge badge-green">OK</span>',
    rejected: '<span class="badge badge-trust">Відхилено</span>',
  };
  return map[status] || map.pending;
};

PP.showToast = (msg, type = "info") => {
  let el = document.getElementById("pp-toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "pp-toast";
    el.className = "pp-toast";
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.dataset.type = type;
  el.classList.add("visible");
  setTimeout(() => el.classList.remove("visible"), 3500);
};

/**
 * Shared profile photo UX: pick → preview → Save / Delete (confirm).
 * @returns {{ setSavedPhoto: Function, getLivePhotoUrl: Function }}
 */
PP.bindProfilePhotoControls = ({ uploadFn, deleteFn, getDisplayName, onChange }) => {
  const photoPreview = document.getElementById("profile-photo-preview");
  const photoFallback = document.getElementById("profile-photo-fallback");
  const photoInput = document.getElementById("profile-photo-input");
  const pickBtn = document.getElementById("profile-photo-btn");
  const saveBtn = document.getElementById("profile-photo-save");
  const deleteBtn = document.getElementById("profile-photo-delete");
  const statusEl = document.getElementById("profile-photo-status");

  let savedPhoto = "";
  let pendingFile = null;
  let pendingUrl = "";

  const getInitial = (name) => {
    const parts = String(name || "").trim().split(/\s+/).filter(Boolean);
    return (parts[0]?.[0] || "👤").toUpperCase();
  };

  const showPhoto = (url, name) => {
    if (!photoPreview || !photoFallback) return;
    if (url) {
      photoPreview.src = url;
      photoPreview.hidden = false;
      photoFallback.hidden = true;
    } else {
      photoPreview.removeAttribute("src");
      photoPreview.hidden = true;
      photoFallback.hidden = false;
      photoFallback.textContent = getInitial(name);
    }
  };

  const setStatus = (text, kind = "") => {
    if (!statusEl) return;
    if (!text) {
      statusEl.hidden = true;
      statusEl.textContent = "";
      statusEl.removeAttribute("data-kind");
      return;
    }
    statusEl.hidden = false;
    statusEl.textContent = text;
    if (kind) statusEl.dataset.kind = kind;
    else statusEl.removeAttribute("data-kind");
  };

  const syncChrome = () => {
    const name = getDisplayName?.() || "";
    const hasSaved = Boolean(savedPhoto);
    const hasPending = Boolean(pendingFile);

    if (pickBtn) {
      pickBtn.textContent = hasSaved || hasPending ? "Змінити фото" : "Додати фото";
    }
    if (saveBtn) {
      saveBtn.disabled = !hasPending;
      saveBtn.hidden = false;
    }
    if (deleteBtn) {
      deleteBtn.hidden = !(hasSaved || hasPending);
    }

    if (hasPending) {
      showPhoto(pendingUrl, name);
      setStatus("Фото не збережено", "pending");
    } else if (hasSaved) {
      showPhoto(savedPhoto, name);
      setStatus("Фото збережено", "saved");
    } else {
      showPhoto("", name);
      setStatus("");
    }
    onChange?.();
  };

  const setSavedPhoto = (url) => {
    if (pendingUrl) {
      URL.revokeObjectURL(pendingUrl);
      pendingUrl = "";
    }
    pendingFile = null;
    if (photoInput) photoInput.value = "";
    savedPhoto = url || "";
    syncChrome();
  };

  const getLivePhotoUrl = () => {
    if (pendingUrl) return pendingUrl;
    return savedPhoto || "";
  };

  if (pickBtn && photoInput) {
    pickBtn.addEventListener("click", () => photoInput.click());
    photoInput.addEventListener("change", () => {
      const file = photoInput.files?.[0];
      if (!file) return;
      if (file.size > 5 * 1024 * 1024) {
        alert("Максимальний розмір фото — 5 МБ");
        photoInput.value = "";
        return;
      }
      if (pendingUrl) URL.revokeObjectURL(pendingUrl);
      pendingFile = file;
      pendingUrl = URL.createObjectURL(file);
      syncChrome();
    });
  }

  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      if (!pendingFile || !uploadFn) return;
      saveBtn.disabled = true;
      if (pickBtn) pickBtn.disabled = true;
      if (deleteBtn) deleteBtn.disabled = true;
      try {
        const updated = await uploadFn(pendingFile);
        const photo = PP.resolveMediaUrl?.(updated?.photo) || updated?.photo || "";
        setSavedPhoto(photo);
        PP.showToast("Фото збережено");
      } catch (err) {
        alert(err.message || "Не вдалося зберегти фото");
        syncChrome();
      } finally {
        if (pickBtn) pickBtn.disabled = false;
        if (deleteBtn) deleteBtn.disabled = false;
      }
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {
      const hasPending = Boolean(pendingFile);
      const hasSaved = Boolean(savedPhoto);
      if (!hasPending && !hasSaved) return;

      if (hasPending && !hasSaved) {
        if (!confirm("Скасувати обране фото?")) return;
        if (pendingUrl) URL.revokeObjectURL(pendingUrl);
        pendingFile = null;
        pendingUrl = "";
        if (photoInput) photoInput.value = "";
        syncChrome();
        return;
      }

      if (hasPending && hasSaved) {
        if (!confirm("Скасувати нове фото і залишити збережене?")) return;
        if (pendingUrl) URL.revokeObjectURL(pendingUrl);
        pendingFile = null;
        pendingUrl = "";
        if (photoInput) photoInput.value = "";
        syncChrome();
        return;
      }

      if (!confirm("Видалити фото профілю?")) return;
      deleteBtn.disabled = true;
      if (pickBtn) pickBtn.disabled = true;
      if (saveBtn) saveBtn.disabled = true;
      try {
        if (deleteFn) await deleteFn();
        setSavedPhoto("");
        PP.showToast("Фото видалено");
      } catch (err) {
        alert(err.message || "Не вдалося видалити фото");
        syncChrome();
      } finally {
        if (pickBtn) pickBtn.disabled = false;
        if (deleteBtn) deleteBtn.disabled = false;
      }
    });
  }

  syncChrome();
  return { setSavedPhoto, getLivePhotoUrl, syncChrome };
};

PP.initCabinetPage = async () => {
  const path = PP.normalizePath(location.pathname);
  if (path.startsWith("/cabinet/parent")) {
    if (!(await PP.requireAuth(["parent"]))) return;
    PP.initCabinetNav(PP.PARENT_NAV, path);
    if (path === "/cabinet/parent" || path.endsWith("/parent")) PP.initParentDashboard?.();
    if (path.includes("/search")) PP.initCatalog?.();
    if (path.includes("/profile")) PP.initParentProfile?.();
    if (path.includes("/favorites")) PP.initParentFavorites?.();
    if (path.includes("/chat")) PP.initChatPage?.("parent");
    if (path.includes("/payments")) PP.initParentPayments?.();
    if (path.includes("/reviews")) PP.initParentReviews?.();
    return;
  }
  if (path.startsWith("/cabinet/nanny")) {
    if (!(await PP.requireAuth(["nanny"]))) return;
    PP.initCabinetNav(PP.NANNY_NAV, path);
    if (path === "/cabinet/nanny" || path.endsWith("/nanny")) PP.initNannyDashboard?.();
    if (path.includes("/profile")) PP.initNannyProfile?.();
    if (path.includes("/calendar")) PP.initNannyCalendar?.();
    if (path.includes("/documents")) PP.initNannyDocuments?.();
    if (path.includes("/messages")) PP.initChatPage?.("nanny");
    if (path.includes("/rating")) PP.initNannyRating?.();
    return;
  }
  if (PP.isAdminPath(path)) {
    if (!(await PP.requireAuth(["admin"]))) return;
    PP.initCabinetNav(PP.ADMIN_NAV, path);
    if (path === "/admin" || path.endsWith("/admin")) PP.initAdminDashboard?.();
    if (path.includes("/users")) PP.initAdminUsers?.();
    if (path.includes("/profiles")) PP.initAdminProfiles?.();
    if (path.includes("/documents")) PP.initAdminDocuments?.();
    if (path.includes("/finance")) PP.initAdminFinance?.();
    if (path.includes("/analytics")) PP.initAdminAnalytics?.();
    if (path.includes("/content")) PP.initAdminContent?.();
    if (path.includes("/messages")) PP.initChatPage?.("admin");
  }
};
