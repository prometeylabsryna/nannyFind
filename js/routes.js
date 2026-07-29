/* Маршрути згідно карти сайту */
window.PP = window.PP || {};

PP.isLocalDev = () => {
  const host = window.location.hostname;
  return host === "localhost" || host === "127.0.0.1";
};

PP.useMockFallback = () => PP.isLocalDev();

PP.ROUTES = {
  home: "/",
  catalog: "/nanny/",
  nanny: (id) => `/nanny/${id}`,
  city: (slug) => `/city/${slug}/`,
  howItWorks: "/how-it-works",
  blog: "/blog/",
  blogPost: (slug) => `/blog/${slug}`,
  faq: "/faq/",
  contacts: "/contacts",
  services: "/services/",
  register: "/register",
  login: "/login",
  forgotPassword: "/forgot-password",
  resetPassword: "/reset-password",
  publicOffer: "/public-offer",
  terms: "/terms-of-service",
  privacy: "/privacy-policy",
  cookies: "/cookie-policy",
  parentCabinet: "/cabinet/parent/",
  parentSearch: "/cabinet/parent/search",
  parentProfile: "/cabinet/parent/profile",
  parentFavorites: "/cabinet/parent/favorites",
  parentChat: "/cabinet/parent/chat",
  parentPayments: "/cabinet/parent/payments",
  parentReviews: "/cabinet/parent/reviews",
  nannyCabinet: "/cabinet/nanny/",
  nannyProfile: "/cabinet/nanny/profile",
  nannyCalendar: "/cabinet/nanny/calendar",
  nannyDocuments: "/cabinet/nanny/documents",
  nannyMessages: "/cabinet/nanny/messages",
  nannyRating: "/cabinet/nanny/rating",
  admin: "/admin/",
  adminUsers: "/admin/users",
  adminProfiles: "/admin/profiles",
  adminFinance: "/admin/finance",
  adminAnalytics: "/admin/analytics",
  adminMessages: "/admin/messages",
};

PP.CITY_LOCATIVE = {
  Київ: "у Києві",
  Львів: "у Львові",
  Дніпро: "у Дніпрі",
  Харків: "у Харкові",
  Одеса: "в Одесі",
};

PP.cityLocative = (name) => PP.CITY_LOCATIVE[name] || `у ${name}`;

PP.normalizePath = (path = location.pathname) => {
  let p = (path || "/").split("?")[0];
  if (p.length > 1 && p.endsWith("/")) p = p.slice(0, -1);
  return p;
};

PP.pathNannyId = () => {
  const m = PP.normalizePath().match(/^\/nanny\/(\d+)$/);
  if (m) return m[1];
  return new URLSearchParams(location.search).get("id");
};

PP.pathBlogSlug = () => {
  const m = PP.normalizePath().match(/^\/blog\/([\w-]+)$/);
  if (m && m[1] !== "index") return m[1];
  const el = document.getElementById("blog-article");
  return el?.dataset?.slug || null;
};

PP.loginUrl = (next = location.pathname + location.search) =>
  `${PP.ROUTES.login}?next=${encodeURIComponent(next)}`;

/* chatHref defined in api.js after auth helpers */

PP.authHomeForRole = (role) => {
  if (role === "nanny") return PP.ROUTES.nannyCabinet;
  if (PP.isPlatformAdmin?.() || role === "admin") return PP.ROUTES.admin;
  return PP.ROUTES.parentCabinet;
};

PP.isAuthPage = (path = location.pathname) => {
  const p = PP.normalizePath(path);
  return [PP.ROUTES.login, PP.ROUTES.register, PP.ROUTES.forgotPassword, PP.ROUTES.resetPassword].includes(p)
    || p.endsWith("/login.html")
    || p.endsWith("/register.html");
};

PP.isCabinetPath = (path = location.pathname) => PP.normalizePath(path).startsWith("/cabinet/");
