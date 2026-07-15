/* Ролі та режими: гість (інкогніто), батьки, няня */
window.PP = window.PP || {};

PP.ROLE = {
  GUEST: "guest",
  PARENT: "parent",
  NANNY: "nanny",
  ADMIN: "admin",
};

PP.ROLE_LABELS = {
  guest: "Гість",
  parent: "Батьки",
  nanny: "Няня",
  admin: "Адмін",
};

PP.ROLE_HINTS = {
  guest: "Перегляд без реєстрації",
  parent: "Пошук, чат, підписка",
  nanny: "Профіль, календар, повідомлення",
  admin: "Модерація платформи",
};

PP.CABINET_LINKS = {
  parent: [PP.ROUTES.parentCabinet, "Кабінет батьків"],
  nanny: [PP.ROUTES.nannyCabinet, "Кабінет няні"],
  admin: [PP.ROUTES.admin, "Панель"],
};

PP.isLoggedInUser = () => {
  const access = PP._token?.();
  const hasRefresh = !!localStorage.getItem("pp-refresh-token");
  return !!(access && !PP.isTokenExpired(access)) || hasRefresh;
};

PP.getViewMode = () => {
  if (!PP.isLoggedInUser()) return PP.ROLE.GUEST;
  if (PP.isPlatformAdmin?.()) return PP.ROLE.ADMIN;
  const role = PP.getSessionRole?.();
  if (role === PP.ROLE.NANNY) return PP.ROLE.NANNY;
  if (role === PP.ROLE.ADMIN) return PP.ROLE.ADMIN;
  if (role === PP.ROLE.PARENT) return PP.ROLE.PARENT;
  return PP.ROLE.GUEST;
};

PP.isGuestMode = () => PP.getViewMode() === PP.ROLE.GUEST;
PP.canUseParentFeatures = () => PP.getViewMode() === PP.ROLE.PARENT;
PP.canUseNannyFeatures = () => PP.getViewMode() === PP.ROLE.NANNY;

PP.getRoleLabel = (mode) => PP.ROLE_LABELS[mode || PP.getViewMode()] || PP.ROLE_LABELS.guest;

PP.getRoleHint = (mode) => PP.ROLE_HINTS[mode || PP.getViewMode()] || "";

PP.getCabinetInfo = () => {
  const mode = PP.getViewMode();
  if (mode === PP.ROLE.GUEST) return null;
  return PP.CABINET_LINKS[mode] || null;
};

PP.loginUrl = (nextPath) => {
  const next = nextPath || `${location.pathname}${location.search}`;
  return `${PP.ROUTES.login}?next=${encodeURIComponent(next)}`;
};

PP.registerUrl = (role) => {
  if (role === PP.ROLE.NANNY || role === "nanny") return `${PP.ROUTES.register}?role=nanny`;
  if (role === PP.ROLE.PARENT || role === "parent") return `${PP.ROUTES.register}?role=parent`;
  return PP.ROUTES.register;
};

PP.requireParentForAction = async (actionLabel = "Дія") => {
  await PP.waitForSession?.();
  const mode = PP.getViewMode();
  if (mode === PP.ROLE.PARENT) return true;
  const here = `${location.pathname}${location.search}`;
  if (mode === PP.ROLE.GUEST) {
    location.href = PP.loginUrl(here);
    return false;
  }
  if (mode === PP.ROLE.NANNY) {
    alert(
      `«${actionLabel}» доступно лише для акаунта батьків. Зареєструйтесь як батьки або увійдіть під іншим email.`
    );
    location.href = `${PP.ROUTES.login}?next=${encodeURIComponent(here)}&reauth=1`;
    return false;
  }
  return false;
};

PP.syncFavoriteButtons = async (root = document) => {
  if (!PP.canUseParentFeatures()) return;
  let favIds = new Set();
  try {
    const favs = await PP.fetchFavorites();
    favIds = new Set((favs || []).map((f) => String(f.nanny?.id ?? f.nanny_id ?? f.id)));
  } catch {
    return;
  }
  root.querySelectorAll(".nanny-card-fav[data-nanny-id], #profile-fav-btn[data-nanny-id]").forEach((btn) => {
    PP.setFavoriteButtonState(btn, favIds.has(String(btn.dataset.nannyId)));
  });
};

PP.initFavoriteButtons = () => {
  if (document.body.dataset.favInit) return;
  document.body.dataset.favInit = "1";

  document.body.addEventListener("click", async (e) => {
    const btn = e.target.closest(".nanny-card-fav, #profile-fav-btn");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();

    const nannyId = btn.dataset.nannyId;
    if (!nannyId) return;
    if (!(await PP.requireParentForAction("Обране"))) return;

    const isActive = btn.classList.contains("active");
    btn.disabled = true;
    try {
      if (isActive) {
        await PP.removeFavorite(nannyId);
        PP.setFavoriteButtonState(btn, false);
        PP.showToast?.("Прибрано з обраного");
      } else {
        await PP.addFavorite(nannyId);
        PP.setFavoriteButtonState(btn, true, { pulse: true });
        PP.showToast?.("Додано в обране");
      }
      PP.refreshFavoritesCount?.();
      document.dispatchEvent(
        new CustomEvent("pp:favorite-changed", { detail: { nannyId, active: !isActive } })
      );
    } catch (err) {
      alert(err.message || "Помилка");
    } finally {
      btn.disabled = false;
    }
  });
};

PP.applyRoleHeader = () => {
  const mode = PP.getViewMode();
  const loggedIn = mode !== PP.ROLE.GUEST;
  const cabinet = PP.getCabinetInfo();

  const badge = document.getElementById("header-role-badge");
  if (badge) {
    badge.textContent = PP.getRoleLabel(mode);
    badge.title = `Ваша роль: ${PP.getRoleLabel(mode)}. ${PP.getRoleHint(mode)}`;
    badge.setAttribute("aria-label", `Роль: ${PP.getRoleLabel(mode)}`);
    badge.dataset.role = mode;
    badge.hidden = false;
  }

  const badgeMobile = document.getElementById("header-role-badge-mobile");
  if (badgeMobile) {
    badgeMobile.textContent = PP.getRoleLabel(mode);
    badgeMobile.title = `Ваша роль: ${PP.getRoleLabel(mode)}. ${PP.getRoleHint(mode)}`;
    badgeMobile.setAttribute("aria-label", `Роль: ${PP.getRoleLabel(mode)}`);
    badgeMobile.dataset.role = mode;
    badgeMobile.hidden = false;
  }

  const reg = document.getElementById("register-link");
  const regM = document.getElementById("register-link-mobile");
  [reg, regM].forEach((el) => {
    if (!el) return;
    el.hidden = loggedIn;
    el.toggleAttribute("aria-hidden", loggedIn);
  });
};
