/* REST API client — Поміч поруч */
window.PP = window.PP || {};

PP.resolveApiBase = () => {
  if (window.PP_API_BASE) return window.PP_API_BASE.replace(/\/$/, "");
  const { protocol, hostname, port } = window.location;
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    const apiPort = port === "8082" ? "8001" : port === "8080" ? "8000" : "8001";
    return `${protocol}//${hostname}:${apiPort}/api/v1`;
  }
  return `${protocol}//${hostname}/api/v1`;
};

PP.API_BASE = PP.resolveApiBase();

PP.resolveMediaUrl = (url) => {
  if (!url) return "";
  if (/^(https?:|blob:|data:)/i.test(url)) return url;
  const base = PP.API_BASE.replace(/\/api\/v1\/?$/, "");
  return url.startsWith("/") ? `${base}${url}` : `${base}/${url}`;
};

PP.DOC_TYPES = {
  passport: "Паспорт (скан)",
  ipn: "ІПН",
  first_aid: "Сертифікат першої допомоги",
  medical_cert: "Медичний сертифікат",
  education_cert: "Освітній / педагогічний",
  criminal_record: "Довідка про несудимість",
  other: "Інший документ",
};

PP.REQUIRED_NANNY_DOCS = ["passport", "ipn"];

PP._token = () => localStorage.getItem("pp-access-token");

PP.isAdminPath = (path = location.pathname) => {
  const p = (path || "").split("?")[0];
  return p === "/admin" || p.startsWith("/admin/");
};

PP.isProtectedPath = () =>
  location.pathname.includes("/cabinet/") || PP.isAdminPath();

PP.isAuthPublicPath = (path) =>
  path.startsWith("/auth/login")
  || path.startsWith("/auth/register")
  || path.startsWith("/auth/token/refresh")
  || path.startsWith("/auth/oauth")
  || path.startsWith("/auth/password/");

PP.parseJwtExp = (token) => {
  try {
    const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
    return payload.exp * 1000;
  } catch {
    return 0;
  }
};

PP.isTokenExpired = (token, skewMs = 30000) => {
  if (!token) return true;
  const exp = PP.parseJwtExp(token);
  return !exp || Date.now() >= exp - skewMs;
};

PP.isLoggedIn = () => !!(PP._token() || localStorage.getItem("pp-refresh-token"));

PP.hasStoredSession = () =>
  !!(PP._token() || localStorage.getItem("pp-refresh-token"));

PP.clearSession = () => {
  ["pp-access-token", "pp-refresh-token", "pp-role", "pp-user", "pp-is-platform-admin"].forEach((k) =>
    localStorage.removeItem(k)
  );
  PP._sessionBoot = Promise.resolve(false);
  PP._refreshPromise = null;
};

PP.getSessionUser = () => {
  try {
    return JSON.parse(localStorage.getItem("pp-user") || "null");
  } catch {
    return null;
  }
};

PP.isPlatformAdmin = (user = PP.getSessionUser()) => {
  if (user?.is_platform_admin || user?.role === "admin") return true;
  return localStorage.getItem("pp-is-platform-admin") === "1";
};

PP.saveSession = (payload) => {
  if (payload.tokens?.access) localStorage.setItem("pp-access-token", payload.tokens.access);
  if (payload.tokens?.refresh) localStorage.setItem("pp-refresh-token", payload.tokens.refresh);
  if (payload.user?.role) localStorage.setItem("pp-role", payload.user.role);
  if (payload.user) {
    localStorage.setItem("pp-user", JSON.stringify(payload.user));
    localStorage.setItem(
      "pp-is-platform-admin",
      PP.isPlatformAdmin(payload.user) ? "1" : "0"
    );
  }
  PP._refreshPromise = null;
  PP._sessionBoot = Promise.resolve(true);
  if (typeof PP.updateAuthHeader === "function") PP.updateAuthHeader();
};

PP.authHomeForRole = PP.authHomeForRole || ((role, user = PP.getSessionUser()) => {
  if (role === "nanny") return PP.ROUTES.nannyCabinet;
  if (PP.isPlatformAdmin(user) || role === "admin") return PP.ROUTES.admin;
  return PP.ROUTES.parentCabinet;
});

PP.needsParentAccount = (path = "") => PP.normalizePath(path).startsWith("/cabinet/parent");

PP.needsAdminAccount = (path = "") => PP.isAdminPath(path);

PP.resolveChatTarget = (nannyId, role, user) => {
  const isAdmin = PP.isPlatformAdmin(user) || role === "admin";
  const base = isAdmin ? PP.ROUTES.adminMessages : PP.ROUTES.parentChat;
  return nannyId ? `${base}?nanny=${nannyId}` : base;
};

PP.canStartChat = (role, user = PP.getSessionUser()) =>
  role === "parent" || PP.isPlatformAdmin(user) || role === "admin";

PP.resolveChatAccess = async (nannyId) => {
  if (!PP.hasStoredSession()) {
    return PP.loginUrl(PP.resolveChatTarget(nannyId, null));
  }

  await PP.waitForSession();
  let role = PP.getSessionRole();
  if (!role) {
    await PP.syncSessionUser?.();
    role = PP.getSessionRole();
  }
  let user = PP.getSessionUser();
  if (!role && PP._token()) {
    try {
      user = await PP.fetchMe();
      PP.saveSession({
        user,
        tokens: {
          access: PP._token(),
          refresh: localStorage.getItem("pp-refresh-token"),
        },
      });
      role = user.role;
    } catch {
      return PP.loginUrl(PP.resolveChatTarget(nannyId, null, user));
    }
  }

  if (PP.canStartChat(role, user)) {
    return PP.resolveChatTarget(nannyId, role, user);
  }
  return `${PP.ROUTES.login}?next=${encodeURIComponent(PP.resolveChatTarget(nannyId, role, user))}&reauth=1`;
};

PP.chatHref = (nannyId) => {
  const target = PP.resolveChatTarget(nannyId, PP.getSessionRole(), PP.getSessionUser());
  if (!PP.hasStoredSession()) {
    return PP.loginUrl(target);
  }
  const role = PP.getSessionRole();
  const user = PP.getSessionUser();
  if (!PP.canStartChat(role, user)) {
    return `${PP.ROUTES.login}?next=${encodeURIComponent(target)}&reauth=1`;
  }
  return target;
};

PP.getSessionRole = () => {
  const role = localStorage.getItem("pp-role");
  if (role) return role;
  try {
    const user = JSON.parse(localStorage.getItem("pp-user") || "null");
    if (user?.role) {
      localStorage.setItem("pp-role", user.role);
      return user.role;
    }
  } catch { /* ignore */ }
  return null;
};

PP.openChat = async (nannyId) => {
  location.href = await PP.resolveChatAccess(nannyId);
};

PP.refreshToken = async () => {
  if (PP._refreshPromise) return PP._refreshPromise;

  const refreshAtStart = localStorage.getItem("pp-refresh-token");
  if (!refreshAtStart) return { ok: false, status: 0 };

  PP._refreshPromise = (async () => {
    try {
      const res = await fetch(`${PP.API_BASE}/auth/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: refreshAtStart }),
      });
      if (!res.ok) return { ok: false, status: res.status };

      const data = await res.json();
      const refreshNow = localStorage.getItem("pp-refresh-token");
      if (refreshNow !== refreshAtStart) {
        return { ok: false, status: 0, stale: true };
      }

      localStorage.setItem("pp-access-token", data.access);
      if (data.refresh) localStorage.setItem("pp-refresh-token", data.refresh);
      return { ok: true, status: res.status };
    } catch {
      return { ok: false, status: 0 };
    } finally {
      PP._refreshPromise = null;
    }
  })();

  return PP._refreshPromise;
};

PP.syncSessionUser = async () => {
  const token = PP._token();
  if (!token) return null;
  try {
    const res = await fetch(`${PP.API_BASE}/auth/me/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return null;
    const user = await res.json();
    if (user?.role) localStorage.setItem("pp-role", user.role);
    if (user) {
      localStorage.setItem("pp-user", JSON.stringify(user));
      localStorage.setItem("pp-is-platform-admin", PP.isPlatformAdmin(user) ? "1" : "0");
    }
    return user;
  } catch {
    return null;
  }
};

PP.ensureValidSession = async () => {
  const startAccess = PP._token();
  const startRefresh = localStorage.getItem("pp-refresh-token");

  if (!startAccess && !startRefresh) return false;
  if (startAccess && !PP.isTokenExpired(startAccess)) return true;
  if (!startRefresh) {
    if (startAccess && PP.isTokenExpired(startAccess) && PP._token() === startAccess) {
      PP.clearSession();
    }
    return false;
  }

  const result = await PP.refreshToken();

  if (localStorage.getItem("pp-refresh-token") !== startRefresh) {
    const access = PP._token();
    return !!(access && !PP.isTokenExpired(access)) || !!localStorage.getItem("pp-refresh-token");
  }

  if (result.ok) {
    await PP.syncSessionUser();
    return true;
  }
  if (startAccess && !PP.isTokenExpired(startAccess) && PP._token() === startAccess) return true;
  if (result.status === 401 || result.status === 403) {
    if (localStorage.getItem("pp-refresh-token") === startRefresh) {
      PP.clearSession();
    }
    return false;
  }
  return !!localStorage.getItem("pp-refresh-token");
};

PP._sessionBoot = null;
PP._refreshPromise = null;

PP.bootSession = () => {
  if (!PP._sessionBoot) {
    PP._sessionBoot = PP.ensureValidSession();
  }
  return PP._sessionBoot;
};

PP.waitForSession = () => PP.bootSession();

PP.handleAuthFailure = () => {
  if (!PP.hasStoredSession()) return;
  PP.clearSession();
  if (PP.isProtectedPath() && !PP.isAuthPage()) {
    const next = encodeURIComponent(location.pathname + location.search);
    location.href = `${PP.ROUTES.login}?next=${next}`;
  }
  if (typeof PP.updateAuthHeader === "function") PP.updateAuthHeader();
};

PP.apiFetch = async (path, options = {}, retried = false) => {
  const skipAuth = PP.isAuthPublicPath(path);
  if (!skipAuth && PP.hasStoredSession()) {
    await PP.waitForSession();
  }

  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  const token = skipAuth ? null : PP._token();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${PP.API_BASE}${path}`, { ...options, headers });
  } catch (err) {
    const networkErr = new Error("Немає з'єднання з сервером. Перевірте, чи запущено API.");
    networkErr.cause = err;
    throw networkErr;
  }

  const data = await res.json().catch(() => ({}));

  if (res.status === 401 && !retried && !skipAuth && localStorage.getItem("pp-refresh-token")) {
    const refreshed = await PP.refreshToken();
    if (refreshed.ok) return PP.apiFetch(path, options, true);
  }

  if (res.status === 401 && !skipAuth) {
    PP.handleAuthFailure();
  }

  if (!res.ok) {
    const firstFieldError = Object.values(data).find((v) => Array.isArray(v) && v.length)?.[0];
    const msg = data.detail || data.email?.[0] || firstFieldError || "Помилка API";
    const err = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
};

PP.normalizeNanny = (n) => ({
  ...n,
  id: String(n.id),
  photo: PP.resolveMediaUrl(n.photo || n.photo_url || ""),
  certificates: Array.isArray(n.certificates) ? n.certificates : [],
  reviewCount: n.reviewCount ?? n.review_count ?? 0,
  hourlyRate: n.hourlyRate ?? n.hourly_rate ?? 0,
  experienceYears: n.experienceYears ?? n.experience_years ?? 0,
  completedOrders: n.completedOrders ?? n.completed_orders ?? 0,
  familiesCount: n.familiesCount ?? n.families_count ?? 0,
  isVerified: n.isVerified ?? n.is_verified ?? false,
  hasCar: n.hasCar ?? n.has_car ?? false,
  medicalEducation: n.medicalEducation ?? n.medical_education ?? false,
  firstAidCourse: n.firstAidCourse ?? n.first_aid_course ?? false,
});

PP.authRegister = (body) =>
  PP.apiFetch("/auth/register/", { method: "POST", body: JSON.stringify(body) });

PP.authLogin = (email, password) =>
  PP.apiFetch("/auth/login/", { method: "POST", body: JSON.stringify({ email, password }) });

PP.authOAuth = (provider, payload, role = "parent") =>
  PP.apiFetch("/auth/oauth/", {
    method: "POST",
    body: JSON.stringify({ provider, role, ...payload }),
  });

PP.authOAuthStatus = () => PP.apiFetch("/auth/oauth/status/");

PP.authPasswordReset = (email) =>
  PP.apiFetch("/auth/password/reset/", { method: "POST", body: JSON.stringify({ email }) });

PP.authPasswordResetConfirm = (uid, token, newPassword) =>
  PP.apiFetch("/auth/password/reset/confirm/", {
    method: "POST",
    body: JSON.stringify({ uid, token, new_password: newPassword }),
  });

PP.fetchMe = () => PP.apiFetch("/auth/me/");

PP.logout = () => {
  PP.clearSession();
  if (typeof PP.updateAuthHeader === "function") PP.updateAuthHeader();
};

PP.shouldBootSessionEarly = () => true;

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    if (PP.shouldBootSessionEarly()) PP.bootSession();
  });
} else if (PP.shouldBootSessionEarly()) {
  PP.bootSession();
}

PP.fetchNannies = async (filters = {}) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v === "" || v === false || v === null || v === undefined) return;
    if (Array.isArray(v) && v.length) params.set("languages", v.join(","));
    else if (typeof v === "boolean") params.set(k, v ? "true" : "false");
    else params.set(k, v);
  });
  const data = await PP.apiFetch(`/nannies/?${params.toString()}`);
  return (data.results || data).map(PP.normalizeNanny);
};

PP.fetchNanny = async (id) => PP.normalizeNanny(await PP.apiFetch(`/nannies/${id}/`));

PP.fetchParentProfile = () => PP.apiFetch("/parents/profile/");
PP.saveParentProfile = (body) =>
  PP.apiFetch("/parents/profile/", { method: "PATCH", body: JSON.stringify(body) });
PP.uploadParentPhoto = (file) => {
  const fd = new FormData();
  fd.append("photo", file);
  return PP.apiFetch("/parents/profile/", { method: "PATCH", body: fd });
};
PP.deleteParentPhoto = () =>
  PP.apiFetch("/parents/profile/", {
    method: "PATCH",
    body: JSON.stringify({ clear_photo: true }),
  });

PP.normalizeParent = (p) => ({
  ...p,
  name: p.name || `${p.first_name || ""} ${p.last_name || ""}`.trim(),
  photo: PP.resolveMediaUrl(p.photo || ""),
  children_count: p.children_count ?? 0,
});

PP.fetchFavorites = async () => {
  const data = await PP.apiFetch("/parents/favorites/");
  return Array.isArray(data) ? data : (data.results ?? []);
};
PP.addFavorite = (nannyId) =>
  PP.apiFetch("/parents/favorites/", { method: "POST", body: JSON.stringify({ nanny_id: nannyId }) });
PP.removeFavorite = (nannyId) =>
  PP.apiFetch(`/parents/favorites/${nannyId}/`, { method: "DELETE" });

PP.fetchNannyProfile = () => PP.apiFetch("/nannies/me/");
PP.saveNannyProfile = (body) =>
  PP.apiFetch("/nannies/me/", { method: "PATCH", body: JSON.stringify(body) });
PP.uploadNannyPhoto = (file) => {
  const fd = new FormData();
  fd.append("photo", file);
  return PP.apiFetch("/nannies/me/", { method: "PATCH", body: fd });
};
PP.deleteNannyPhoto = () =>
  PP.apiFetch("/nannies/me/", {
    method: "PATCH",
    body: JSON.stringify({ clear_photo: true }),
  });

PP.dateKey = (d) => {
  const date = d instanceof Date ? d : new Date(d);
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
};

PP.parseAvailabilitySlots = (slots) => {
  const list = Array.isArray(slots) ? slots : (slots?.results || []);
  if (!Array.isArray(list)) return {};
  const map = {};
  list.forEach((s) => {
    if (!s?.date) return;
    map[String(s.date).slice(0, 10)] = s.status;
  });
  return map;
};

PP.fetchAvailability = () => PP.apiFetch("/nannies/me/availability/");
PP.saveAvailability = (slots) =>
  PP.apiFetch("/nannies/me/availability/", { method: "PUT", body: JSON.stringify(slots) });

PP.fetchDocuments = () => PP.apiFetch("/nannies/me/documents/");
PP.uploadDocument = (docType, file) => {
  const fd = new FormData();
  fd.append("doc_type", docType);
  fd.append("file", file);
  return PP.apiFetch("/nannies/me/documents/", { method: "POST", body: fd });
};

PP.fetchConversations = () => PP.apiFetch("/chat/conversations/");
PP.startConversation = (nannyId) =>
  PP.apiFetch("/chat/conversations/start/", { method: "POST", body: JSON.stringify({ nanny_id: nannyId }) });
PP.fetchMessages = (convId, opts = {}) => {
  const q = opts.beforeId != null ? `?before_id=${encodeURIComponent(opts.beforeId)}` : "";
  return PP.apiFetch(`/chat/conversations/${convId}/messages/${q}`);
};
PP.sendMessage = (convId, text, file) => {
  const fd = new FormData();
  if (text) fd.append("text", text);
  if (file) fd.append("attachment", file);
  return PP.apiFetch(`/chat/conversations/${convId}/messages/`, { method: "POST", body: fd });
};
PP.markChatRead = (convId) =>
  PP.apiFetch(`/chat/conversations/${convId}/read/`, { method: "POST", body: "{}" });

PP.fetchPricing = () => PP.apiFetch("/payments/plans/");
PP.fetchPaymentProviders = () => PP.apiFetch("/payments/providers/");
PP.checkout = (planCode, provider = "liqpay") =>
  PP.apiFetch("/payments/checkout/", {
    method: "POST",
    body: JSON.stringify({ plan_code: planCode, provider }),
  });
PP.confirmStubPayment = (orderReference) =>
  PP.apiFetch("/payments/stub/confirm/", {
    method: "POST",
    body: JSON.stringify({ order_reference: orderReference }),
  });
PP.fetchSubscriptions = () => PP.apiFetch("/payments/subscriptions/");
PP.unlockContact = (nannyId) =>
  PP.apiFetch("/payments/unlock/", { method: "POST", body: JSON.stringify({ nanny_id: nannyId }) });

PP.submitReview = (nannyId, rating, text) =>
  PP.apiFetch("/reviews/", { method: "POST", body: JSON.stringify({ nanny: nannyId, rating, text }) });
PP.fetchNannyReviews = (nannyId) => PP.apiFetch(`/reviews/nanny/${nannyId}/`);

PP.fetchFAQ = () => PP.apiFetch("/content/faq/");
PP.fetchBlog = () => PP.apiFetch("/content/blog/");
PP.fetchBlogPost = (slug) => PP.apiFetch(`/content/blog/${slug}/`);
PP.fetchReviewableNannies = () => PP.apiFetch("/parents/reviewable/");
PP.fetchCities = () => PP.apiFetch("/geo/cities/");

PP.adminDashboard = () => PP.apiFetch("/admin/dashboard/");
PP.adminUsers = (query = "") => PP.apiFetch(`/admin/users/${query ? "?" + query : ""}`);
PP.adminProfiles = (status = "pending") => PP.apiFetch(`/admin/profiles/?status=${encodeURIComponent(status)}`);
PP.adminDocuments = (status = "pending") => PP.apiFetch(`/admin/documents/?status=${encodeURIComponent(status)}`);
PP.adminPayments = (section = "payments") => PP.apiFetch(`/admin/payments/?section=${section}`);
PP.adminAnalytics = () => PP.apiFetch("/admin/analytics/");
PP.adminModerateProfile = (profileId, action) =>
  PP.apiFetch("/admin/profiles/", { method: "POST", body: JSON.stringify({ profile_id: profileId, action }) });
PP.adminModerateDocument = (documentId, action) =>
  PP.apiFetch("/admin/documents/", { method: "POST", body: JSON.stringify({ document_id: documentId, action }) });
PP.adminUserStatus = (userId, status) =>
  PP.apiFetch("/admin/users/", { method: "PATCH", body: JSON.stringify({ user_id: userId, status }) });

PP.loadApiCatalog = async (filters, onUpdate) => {
  try {
    PP.NANNIES = await PP.fetchNannies(filters);
    onUpdate();
  } catch (e) {
    if (PP.useMockFallback?.()) {
      console.warn("API catalog fallback:", e.message);
      onUpdate();
      return;
    }
    const grid = document.getElementById("catalog-grid");
    if (grid) {
      grid.innerHTML =
        '<div class="card empty-state"><p>Не вдалося завантажити каталог. Перевірте з\'єднання з сервером.</p><button type="button" class="btn btn-secondary" id="catalog-retry">Спробувати знову</button></div>';
      document.getElementById("catalog-retry")?.addEventListener("click", () => location.reload());
    }
  }
};
