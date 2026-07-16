/* CMS blocks from API */
window.PP = window.PP || {};

PP.SITE_BLOCKS = PP.SITE_BLOCKS || {};
PP.SITE_SETTINGS = PP.SITE_SETTINGS || {};

PP.block = (key, fallback = "") => PP.SITE_BLOCKS[key] ?? fallback;

PP.blockVisible = (key, fallback = true) => {
  const v = PP.SITE_BLOCKS[key];
  if (v === undefined || v === null || v === "") return fallback;
  return !["0", "false", "False"].includes(String(v));
};

PP.accentHtml = (text) => {
  if (!text) return "";
  return String(text)
    .replace(/<em>(.*?)<\/em>/gi, "<em>$1</em>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
};

PP.fetchSiteContent = async () => {
  const data = await PP.apiFetch("/content/blocks/");
  PP.SITE_BLOCKS = data.blocks || {};
  PP.SITE_SETTINGS = data.settings || {};
  return data;
};

PP.fetchStaticPage = (key) => PP.apiFetch(`/content/pages/${key}/`);

PP.loadStaticPage = async (key, selectors = {}) => {
  const root = document.querySelector(selectors.body || "[data-static-body]");
  const titleEl = document.querySelector(selectors.title || "[data-static-title]");
  if (!root && !titleEl) return;
  try {
    const page = await PP.fetchStaticPage(key);
    if (titleEl && page.title) titleEl.textContent = page.title;
    if (root && page.body_html) root.innerHTML = page.body_html;
    if (page.title) document.title = `${page.title} — Поміч поруч`;
  } catch (e) {
    console.warn("Static page fallback:", key, e.message);
  }
};

PP.loadPageContent = async () => {
  const path = PP.normalizePath(location.pathname);
  const map = {
    "/how-it-works": "how-it-works",
    "/services": "services",
    "/contacts": "contacts",
    "/public-offer": "public-offer",
    "/terms-of-service": "terms-of-service",
    "/privacy-policy": "privacy-policy",
    "/cookie-policy": "cookie-policy",
    "/how-it-works.html": "how-it-works",
    "/services.html": "services",
    "/contacts.html": "contacts",
    "/public-offer.html": "public-offer",
    "/terms-of-service.html": "terms-of-service",
    "/privacy-policy.html": "privacy-policy",
    "/cookie-policy.html": "cookie-policy",
  };
  const key = map[path];
  if (key) await PP.loadStaticPage(key);
};

PP.applySiteSettings = (root = document) => {
  const settings = PP.SITE_SETTINGS || {};
  const socialMap = {
    instagram: settings.instagram_url,
    facebook: settings.facebook_url,
    tiktok: settings.tiktok_url,
    telegram: settings.telegram_url,
  };
  root.querySelectorAll("[data-social]").forEach((el) => {
    const url = socialMap[el.dataset.social];
    if (url) {
      el.href = url;
      el.hidden = false;
    }
  });

  root.querySelectorAll("[data-settings]").forEach((el) => {
    const key = el.dataset.settings;
    const val = settings[key];
    if (val === undefined || val === null || val === "") return;
    const hrefPrefix = el.dataset.settingsHref;
    if (hrefPrefix !== undefined) {
      const hrefValue = key === "support_phone" ? val.replace(/[^\d+]/g, "") : val;
      el.setAttribute("href", `${hrefPrefix}${hrefValue}`);
    }
    el.textContent = val;
  });
};

PP.applySiteBlocks = (root = document) => {
  root.querySelectorAll("[data-cms]").forEach((el) => {
    const key = el.dataset.cms;
    const val = PP.block(key);
    if (val === undefined || val === null || val === "") return;
    if (el.dataset.cmsHtml === "1" || el.dataset.cmsHtml === "true") {
      el.innerHTML = PP.accentHtml(val);
    } else {
      el.textContent = val;
    }
  });

  root.querySelectorAll("[data-cms-section]").forEach((el) => {
    const key = el.dataset.cmsSection;
    el.hidden = !PP.blockVisible(key, true);
  });

  root.querySelectorAll("[data-cms-attr]").forEach((el) => {
    const key = el.dataset.cms;
    const attr = el.dataset.cmsAttr || "alt";
    const val = PP.block(key);
    if (val) el.setAttribute(attr, val);
  });

  root.querySelectorAll("[data-cms-src]").forEach((el) => {
    const key = el.dataset.cmsSrc;
    const val = PP.block(key);
    if (!val) return;
    el.setAttribute("src", PP.resolveMediaUrl ? PP.resolveMediaUrl(val) : val);
  });
};

PP.renderHomeBenefits = () => {
  const grid = document.getElementById("benefits");
  const section = grid?.closest("section");
  if (section) section.hidden = !PP.blockVisible("home.benefits_section_visible");
  if (!grid) return;
  if (section?.hidden) return;
  const items = [1, 2, 3, 4].map((i) => ({
    icon: PP.block(`home.benefit_${i}_icon`),
    title: PP.block(`home.benefit_${i}_title`),
    desc: PP.block(`home.benefit_${i}_text`),
  }));
  grid.innerHTML = items
    .map(
      (b) =>
        `<div class="card benefit-card"><div class="benefit-icon">${b.icon}</div><h3>${b.title}</h3><p style="font-size:0.875rem;color:var(--text-muted)">${b.desc}</p></div>`
    )
    .join("");
};

PP.renderHomeSteps = () => {
  const grid = document.getElementById("steps");
  const section = grid?.closest("section");
  if (!grid) return;
  if (!PP.blockVisible("home.steps_section_visible")) {
    if (section) section.hidden = true;
    return;
  }
  const title = document.querySelector("[data-cms=\"home.steps_title\"]");
  const subtitle = document.querySelector("[data-cms=\"home.steps_subtitle\"]");
  if (title) title.textContent = PP.block("home.steps_title", title.textContent);
  if (subtitle) subtitle.textContent = PP.block("home.steps_subtitle", subtitle.textContent);

  const steps = [1, 2, 3, 4].map((i) => ({
    step: i,
    title: PP.block(`home.step_${i}_title`),
    desc: PP.block(`home.step_${i}_desc`),
  }));
  grid.innerHTML = steps
    .map(
      (s) =>
        `<div class="card step-card"><div class="step-num">${s.step}</div><h3>${s.title}</h3><p style="font-size:0.875rem;color:var(--text-muted)">${s.desc}</p></div>`
    )
    .join("");
};

PP.initHomeSections = () => {
  ["featured", "cities"].forEach((name) => {
    const el = document.querySelector(`[data-cms-section="home.${name}_section_visible"]`);
    if (el) el.hidden = !PP.blockVisible(`home.${name}_section_visible`);
  });
};

PP.loadSiteContent = async () => {
  try {
    await PP.fetchSiteContent();
  } catch (e) {
    console.warn("CMS fallback:", e.message);
    return;
  }
  PP.applySiteBlocks();
  PP.applySiteSettings();
  PP.renderHomeBenefits();
  PP.renderHomeSteps();
  PP.initHomeSections();
  await PP.loadPageContent?.();

  const meta = document.querySelector('meta[name="description"]');
  if (meta && PP.SITE_SETTINGS.meta_description) {
    meta.setAttribute("content", PP.SITE_SETTINGS.meta_description);
  }
};

PP.afterPartialSwap = (target) => {
  if (!PP.SITE_BLOCKS || !Object.keys(PP.SITE_BLOCKS).length) return;
  if (target.id === "site-header" || target.id === "site-footer" || target.id === "cookie-banner-wrap") {
    PP.applySiteBlocks(target);
    if (target.id === "site-footer") PP.applySiteSettings(target);
  }
};
