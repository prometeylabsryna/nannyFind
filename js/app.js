/* Layout: header, footer, cookie, mobile menu */
window.PP = window.PP || {};

PP.updateAuthHeader = async () => {
  await PP.waitForSession();

  const userRaw = localStorage.getItem("pp-user");
  if (userRaw) {
    try {
      const u = JSON.parse(userRaw);
      if (u.role) localStorage.setItem("pp-role", u.role);
    } catch { /* ignore */ }
  }

  const mode = PP.getViewMode?.() || (PP.isLoggedIn?.() ? (PP.getSessionRole() || "parent") : "guest");
  const loggedIn = mode !== "guest";
  const cab = document.getElementById("cabinet-link");
  const cabM = document.getElementById("cabinet-link-mobile");
  const logoutBtn = document.getElementById("logout-btn");
  const logoutMobile = document.getElementById("logout-btn-mobile");
  const cabinetInfo = PP.getCabinetInfo?.() || {
    parent: ["/cabinet/parent/", "Кабінет батьків"],
    nanny: ["/cabinet/nanny/", "Кабінет няні"],
    admin: ["/admin/", "Панель"],
  }[mode];

  if (loggedIn && cabinetInfo) {
    const [href, label] = cabinetInfo;
    if (cab) {
      cab.href = href;
      cab.textContent = label;
      cab.hidden = false;
      cab.removeAttribute("aria-hidden");
    }
    if (cabM) {
      cabM.href = href;
      cabM.textContent = label;
      cabM.hidden = false;
      cabM.removeAttribute("aria-hidden");
    }
  } else {
    if (cab) {
      cab.href = PP.ROUTES.login;
      cab.textContent = PP.block?.("site.header_btn_login", "Увійти") || "Увійти";
      cab.hidden = false;
      cab.removeAttribute("aria-hidden");
    }
    if (cabM) {
      cabM.href = PP.ROUTES.login;
      cabM.textContent = PP.block?.("site.header_btn_login", "Увійти") || "Увійти";
      cabM.hidden = false;
      cabM.removeAttribute("aria-hidden");
    }
  }

  [logoutBtn, logoutMobile].forEach((btn) => {
    if (!btn) return;
    btn.hidden = !loggedIn;
    btn.toggleAttribute("aria-hidden", !loggedIn);
    btn.onclick = loggedIn
      ? () => {
          PP.logout();
          location.href = "/";
        }
      : null;
  });

  PP.applyRoleHeader?.();
};

PP.bindChatOpenButtons = (root = document) => {
  const grid = root.id === "catalog-grid" ? root : root.querySelector?.("#catalog-grid");
  const host = grid || root;

  if (host && !host.dataset.chatDelegated) {
    host.dataset.chatDelegated = "1";
    host.addEventListener("click", (e) => {
      const link = e.target.closest(".nanny-card-actions .btn-primary, a.chat-open-btn");
      if (!link) return;
      const nannyId = link.dataset.nannyId
        || new URL(link.getAttribute("href") || "", location.origin).searchParams.get("nanny");
      if (!nannyId) return;
      e.preventDefault();
      PP.openChat(nannyId);
    });
  }

  root.querySelectorAll("a.chat-open-btn:not([data-chat-bound])").forEach((link) => {
    link.dataset.chatBound = "1";
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const nannyId = link.dataset.nannyId
        || new URL(link.getAttribute("href") || "", location.origin).searchParams.get("nanny");
      if (nannyId) PP.openChat(nannyId);
    });
  });
};

PP.initLayout = async () => {
  PP.initPageTransitions();

  const path = location.pathname;
  PP.NAV.forEach((l) => {
    document.querySelectorAll(`.header-nav a[href="${l.href}"]`).forEach((a) => {
      if (path === l.href || (l.href !== "/" && path.startsWith(l.href.replace(".html", "")))) {
        a.classList.add("active");
      }
    });
  });

  const burger = document.getElementById("menu-open");
  const close = document.getElementById("menu-close");
  const menu = document.getElementById("mobile-menu");
  if (burger && menu) {
    burger.addEventListener("click", () => { menu.classList.add("open"); document.body.style.overflow = "hidden"; });
    close?.addEventListener("click", () => { menu.classList.remove("open"); document.body.style.overflow = ""; });
    menu.addEventListener("click", (e) => { if (e.target === menu) { menu.classList.remove("open"); document.body.style.overflow = ""; } });
  }

  await PP.updateAuthHeader();
  PP.initFavoriteButtons?.();
};

PP.initCookie = () => {
  const KEY = "pp-cookie-consent";
  if (localStorage.getItem(KEY)) return;
  const banner = document.getElementById("cookie-banner");
  if (!banner) return;
  setTimeout(() => banner.classList.add("visible"), 600);

  const save = (data) => { localStorage.setItem(KEY, JSON.stringify(data)); banner.classList.remove("visible"); };

  document.getElementById("cookie-accept")?.addEventListener("click", () => save({ n: true, a: true, m: true }));
  document.getElementById("cookie-reject")?.addEventListener("click", () => save({ n: true, a: false, m: false }));
  document.getElementById("cookie-settings-btn")?.addEventListener("click", () => {
    document.getElementById("cookie-settings")?.classList.toggle("hidden");
  });
  document.getElementById("cookie-save")?.addEventListener("click", () => {
    save({
      n: true,
      a: document.getElementById("cookie-analytics")?.checked,
      m: document.getElementById("cookie-marketing")?.checked,
    });
  });
};

PP.initFAQ = () => {
  document.querySelectorAll(".faq-item").forEach((item) => {
    const trigger = item.querySelector(".faq-trigger");
    const wrap = item.querySelector(".faq-answer-wrap");
    if (!trigger) return;

    const setOpen = (open) => {
      item.classList.toggle("open", open);
      trigger.setAttribute("aria-expanded", open ? "true" : "false");
      wrap?.setAttribute("aria-hidden", open ? "false" : "true");
    };

    trigger.addEventListener("click", () => setOpen(!item.classList.contains("open")));
  });
};

PP.initCatalog = () => {
  const grid = document.getElementById("catalog-grid");
  if (!grid) return;
  const cloneFilters = (src) => ({
    ...src,
    languages: [...(src.languages || [])],
  });
  let filters = PP.defaultFilters();
  let mobileDraft = cloneFilters(filters);
  let sortBy = "rating";
  const params = new URLSearchParams(location.search);
  if (params.get("city")) filters.city = params.get("city");
  mobileDraft = cloneFilters(filters);

  const desktop = document.getElementById("filters-desktop");
  const mobile = document.getElementById("filters-mobile");
  const panel = document.getElementById("filters-mobile-panel");
  const toggle = document.getElementById("filters-toggle");
  const toggleClosedLabel = toggle?.textContent?.trim() || "Показати фільтри";

  const sortList = (list) => {
    const arr = [...list];
    if (sortBy === "price_asc") return arr.sort((a, b) => a.hourlyRate - b.hourlyRate);
    if (sortBy === "price_desc") return arr.sort((a, b) => b.hourlyRate - a.hourlyRate);
    if (sortBy === "experience") return arr.sort((a, b) => b.experienceYears - a.experienceYears);
    return arr.sort((a, b) => b.rating - a.rating);
  };

  const runUpdate = () => {
    if (typeof PP.loadApiCatalog === "function") {
      PP.loadApiCatalog(filters, update);
    } else {
      update();
    }
  };

  const onDesktopChange = () => runUpdate();

  const syncDesktop = () => {
    PP.renderFilters(desktop, filters, onDesktopChange);
  };

  const syncMobileDraft = () => {
    PP.renderFilters(mobile, mobileDraft, () => {});
  };

  const setMobileOpen = (open) => {
    if (!panel) return;
    panel.classList.toggle("open", open);
    document.body.classList.toggle("filters-mobile-open", open);
    if (toggle) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "Сховати фільтри" : toggleClosedLabel;
    }
  };

  const applyFilters = (next) => {
    filters = cloneFilters(next);
    syncDesktop();
    runUpdate();
  };

  const resetFilters = () => {
    filters = PP.defaultFilters();
    mobileDraft = cloneFilters(filters);
    syncDesktop();
    syncMobileDraft();
    runUpdate();
  };

  const update = () => {
    const raw = PP.filterNannies(filters);
    const count = document.getElementById("results-count");
    if (count) {
      const n = raw.length;
      const word = n === 1 ? "профіль" : n >= 2 && n <= 4 ? "профілі" : "профілів";
      count.innerHTML = `<span class="catalog-results-num">${n}</span> ${word} знайдено`;
    }
    if (!raw.length) {
      grid.innerHTML = `<div class="card empty-state"><p>За фільтрами нічого не знайдено</p><button type="button" class="btn btn-secondary" id="reset-filters">Скинути</button></div>`;
      document.getElementById("reset-filters")?.addEventListener("click", resetFilters);
      return;
    }
    const list = sortList(raw);
    grid.innerHTML = list.map((n) => PP.renderNannyCard(n)).join("");
    PP.bindChatOpenButtons?.(grid);
    PP.syncFavoriteButtons?.(grid);
  };

  syncDesktop();
  syncMobileDraft();
  runUpdate();

  if (!grid.dataset.chatBound) {
    grid.dataset.chatBound = "1";
    PP.bindChatOpenButtons(grid);
  }

  const sortRoot = document.getElementById("catalog-sort");
  if (sortRoot) {
    const trigger = sortRoot.querySelector(".sort-dropdown-trigger");
    const menu = sortRoot.querySelector(".sort-dropdown-menu");
    const valueEl = sortRoot.querySelector(".sort-dropdown-value");
    const options = sortRoot.querySelectorAll(".sort-dropdown-option");

    const closeMenu = () => {
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      sortRoot.classList.remove("is-open");
    };

    const openMenu = () => {
      menu.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      sortRoot.classList.add("is-open");
    };

    const selectOption = (option) => {
      sortBy = option.dataset.value;
      valueEl.textContent = option.textContent.trim();
      options.forEach((item) => {
        const selected = item === option;
        item.classList.toggle("is-selected", selected);
        item.setAttribute("aria-selected", selected ? "true" : "false");
      });
      closeMenu();
      update();
    };

    trigger?.addEventListener("click", (e) => {
      e.stopPropagation();
      if (menu.hidden) openMenu();
      else closeMenu();
    });

    options.forEach((option) => {
      option.addEventListener("click", () => selectOption(option));
      option.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectOption(option);
        }
      });
    });

    document.addEventListener("click", (e) => {
      if (!sortRoot.contains(e.target)) closeMenu();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeMenu();
        if (panel?.classList.contains("open")) setMobileOpen(false);
      }
    });
  } else {
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && panel?.classList.contains("open")) setMobileOpen(false);
    });
  }

  document.getElementById("filters-reset-desktop")?.addEventListener("click", resetFilters);

  document.getElementById("filters-apply-mobile")?.addEventListener("click", () => {
    applyFilters(mobileDraft);
    setMobileOpen(false);
  });

  document.getElementById("filters-reset-mobile")?.addEventListener("click", () => {
    mobileDraft = PP.defaultFilters();
    syncMobileDraft();
    applyFilters(mobileDraft);
    setMobileOpen(false);
  });

  document.getElementById("filters-mobile-close")?.addEventListener("click", () => {
    setMobileOpen(false);
  });

  panel?.addEventListener("click", (e) => {
    if (e.target === panel) setMobileOpen(false);
  });

  toggle?.addEventListener("click", () => {
    const willOpen = !panel?.classList.contains("open");
    if (willOpen) {
      mobileDraft = cloneFilters(filters);
      syncMobileDraft();
    }
    setMobileOpen(willOpen);
  });
};

PP.initProfile = async () => {
  await PP.waitForSession?.();
  const id = PP.pathNannyId();
  let nanny = null;
  if (typeof PP.fetchNanny === "function" && id) {
    try {
      nanny = await PP.fetchNanny(id);
      nanny.id = String(nanny.id);
    } catch {
      if (PP.useMockFallback?.()) nanny = PP.getNanny(id);
    }
  } else if (PP.useMockFallback?.()) {
    nanny = PP.getNanny(id);
  }
  const root = document.getElementById("profile-root");
  if (!nanny || !root) {
    if (root) root.innerHTML = '<div class="container"><div class="card empty-state"><p>Профіль не знайдено</p><a href="/nanny/" class="btn btn-primary">До каталогу</a></div></div>';
    return;
  }
  let reviews = [];
  try {
    const apiReviews = await PP.fetchNannyReviews(id);
    reviews = (apiReviews || []).map((r) => ({
      author: r.author || r.author_name || "Батьки",
      rating: r.rating,
      text: r.text || r.comment || "",
    }));
  } catch {
    if (PP.useMockFallback?.()) reviews = PP.REVIEWS[id] || [];
  }
  const mode = PP.getViewMode?.() || "guest";
  const favBlock = mode === "parent"
    ? `<button type="button" class="btn btn-secondary btn-block profile-fav-btn" id="profile-fav-btn" data-nanny-id="${nanny.id}">${PP.favHeartIcon()}<span class="fav-btn-label">В обране</span></button>`
    : mode === "guest"
      ? `<a href="${PP.loginUrl(location.pathname + location.search)}" class="btn btn-secondary btn-block profile-fav-btn">${PP.favHeartIcon()}<span class="fav-btn-label">Увійти для обраного</span></a>`
      : `<p class="profile-phone-hint profile-sidebar-hint">Обране доступне лише для акаунта батьків.</p>`;
  const badges = [
    nanny.isVerified ? '<span class="badge badge-green">✓ Перевірено</span>' : "",
    nanny.hasCar ? '<span class="badge badge-trust">🚗 Авто</span>' : "",
    nanny.medicalEducation ? '<span class="badge badge-trust">⚕ Мед. освіта</span>' : "",
    nanny.firstAidCourse ? '<span class="badge badge-green">+ Перша допомога</span>' : "",
  ].filter(Boolean).join(" ");

  root.innerHTML = `
    <div class="profile-layout">
      <div>
        <div class="card profile-hero-card">
          <div class="profile-hero-photo">
            <img src="${nanny.photo}" alt="${nanny.name}" width="560" height="700" decoding="async">
          </div>
          <div class="profile-hero-body">
            <div class="profile-hero-head">
              <div>
                <h1 class="section-title profile-hero-name">${nanny.name}</h1>
                <p class="nanny-card-meta">${nanny.city}, ${nanny.district} · ${nanny.age} років</p>
              </div>
              <div class="profile-hero-pricing">
                <div class="nanny-card-price profile-hero-rate">${PP.formatPrice(nanny.hourlyRate)}/год</div>
                <div class="nanny-card-rating profile-hero-rating">${PP.stars(nanny.rating)} <strong>${nanny.rating}</strong> <span class="nanny-card-meta">(${nanny.reviewCount})</span></div>
              </div>
            </div>
            <div class="profile-hero-badges">${badges}</div>
            <p class="profile-hero-desc">${nanny.description}</p>
            <div class="profile-stats">
              <div class="profile-stat"><div class="profile-stat-value">${nanny.experienceYears}</div><div class="profile-stat-label">років досвіду</div></div>
              <div class="profile-stat"><div class="profile-stat-value">${nanny.languages.length}</div><div class="profile-stat-label">мови</div></div>
              <div class="profile-stat"><div class="profile-stat-value">${nanny.reviewCount}</div><div class="profile-stat-label">відгуків</div></div>
            </div>
            <div class="profile-hero-certs">
              ${nanny.certificates.map((c) => `<span class="badge badge-green">${c}</span>`).join("")}
            </div>
            <p class="nanny-card-meta profile-hero-langs">Мови: ${nanny.languages.join(", ")}</p>
          </div>
        </div>
        <h2 class="section-title" style="font-size:1.25rem;margin:1.5rem 0 1rem">Відгуки</h2>
        ${reviews.length ? reviews.map((r) => `
          <div class="card review-item">
            <div class="review-item-header"><strong>${r.author}</strong>${PP.stars(r.rating)}</div>
            <p style="font-size:0.875rem;color:var(--text-muted);line-height:1.6">${r.text}</p>
          </div>`).join("") : '<div class="card empty-state"><p>Ще немає відгуків</p></div>'}
      </div>
      <aside class="card profile-sidebar">
        <h3 class="profile-sidebar-title">Календар зайнятості</h3>
        <div id="profile-cal" class="profile-sidebar-cal"></div>
        <div class="profile-sidebar-actions">
          <a href="${PP.chatHref(nanny.id)}" data-nanny-id="${nanny.id}" class="btn btn-primary btn-block chat-open-btn profile-sidebar-cta">💬 Написати</a>
          <div id="profile-phone" class="profile-phone-block"></div>
          ${favBlock}
        </div>
      </aside>
    </div>`;
  PP.renderMiniCalendar(nanny.availability, document.getElementById("profile-cal"), { showMonth: true, days: 21 });

  PP.initProfilePhone?.(nanny.id, nanny.phone);
  PP.syncFavoriteButtons?.(document.getElementById("profile-root") || document);

  PP.bindChatOpenButtons?.(document.getElementById("profile-root") || document);

  const cta = document.getElementById("profile-cta");
  if (cta) {
    cta.href = PP.chatHref(nanny.id);
    cta.dataset.nannyId = nanny.id;
    cta.classList.add("chat-open-btn");
    PP.bindChatOpenButtons?.(cta.parentElement || document);
  }
};

PP.initReview = () => {
  const stars = document.querySelectorAll(".review-stars-input button");
  let rating = 0;
  stars.forEach((btn, i) => {
    btn.addEventListener("click", () => {
      rating = i + 1;
      stars.forEach((s, j) => s.classList.toggle("active", j < rating));
      document.getElementById("rating-input").value = rating;
    });
  });
};

PP.initPageTransitions = () => { /* handled natively via @view-transition CSS */ };
