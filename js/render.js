/* Render helpers */
window.PP = window.PP || {};

PP.stars = (rating) => {
  let s = "";
  for (let i = 1; i <= 5; i++) s += i <= Math.floor(rating) ? "★" : "☆";
  return `<span class="stars">${s}</span>`;
};

PP.nannyPhotoInitial = (name) => {
  const parts = String(name || "").trim().split(/\s+/).filter(Boolean);
  return (parts[0]?.[0] || "👤").toUpperCase();
};

PP.favHeartIcon = () =>
  `<svg class="fav-heart" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>`;

PP.setFavoriteButtonState = (btn, active, opts = {}) => {
  if (!btn) return;
  const pulse = opts.pulse === true;
  btn.classList.toggle("active", active);
  btn.setAttribute("aria-label", active ? "Прибрати з обраного" : "Додати в обране");
  const label = btn.querySelector(".fav-btn-label");
  if (label) label.textContent = active ? "В обраному" : "В обране";
  if (!btn.querySelector(".fav-heart")) {
    const icon = PP.favHeartIcon();
    if (label) {
      btn.insertAdjacentHTML("afterbegin", icon);
    } else {
      btn.innerHTML = icon;
    }
  }
  const heart = btn.querySelector(".fav-heart");
  if (heart) {
    heart.classList.remove("fav-heart--pulse");
    if (active && pulse) {
      void heart.offsetWidth;
      heart.classList.add("fav-heart--pulse");
    }
  }
};

PP.renderNannyCard = (n, opts = {}) => {
  const compact = opts.compact === true;
  const cls = compact ? "nanny-card nanny-card--compact" : "nanny-card";
  const cal = "";
  const photo = n.photo || "";
  const photoMarkup = photo
    ? `<img src="${photo}" alt="${n.name}" loading="lazy" width="400" height="400">`
    : `<span class="nanny-card-photo-fallback" aria-hidden="true">${PP.nannyPhotoInitial(n.name)}</span>`;
  return `
<article class="card card-hover ${cls}">
  <div class="nanny-card-photo">
    <a href="${PP.ROUTES.nanny(n.id)}" class="nanny-card-photo-link" tabindex="-1">
      ${photoMarkup}
    </a>
    ${n.isVerified ? '<span class="badge badge-green nanny-card-verified">✓ Перевірено</span>' : ""}
    <button type="button" class="nanny-card-fav" data-nanny-id="${n.id}" aria-label="Додати в обране">${PP.favHeartIcon()}</button>
    <div class="nanny-card-photo-overlay">
      <h3 class="nanny-card-name"><a href="${PP.ROUTES.nanny(n.id)}">${n.name}</a></h3>
      <div class="nanny-card-photo-rating">
        ${PP.stars(n.rating)}<strong>${n.rating}</strong><span class="nanny-card-photo-reviews">(${n.reviewCount} відг.)</span>
      </div>
    </div>
  </div>
  <div class="nanny-card-body">
    <div class="nanny-card-row">
      <p class="nanny-card-meta">${n.city}, ${n.district} · ${n.age} р.</p>
      <span class="nanny-card-price-inline">${PP.formatPrice(n.hourlyRate)}<small>/год</small></span>
    </div>
    <div class="nanny-card-tags">
      <span class="nanny-card-tag">${n.experienceYears} р. досвіду</span>
      ${n.certificates.slice(0, 2).map((c) => `<span class="nanny-card-tag">${c}</span>`).join("")}
    </div>
    ${cal}
    <div class="nanny-card-actions">
      <a href="${PP.ROUTES.nanny(n.id)}" class="btn btn-secondary">Профіль</a>
      <a href="${PP.chatHref(n.id)}" data-nanny-id="${n.id}" class="btn btn-primary chat-open-btn">Написати</a>
    </div>
  </div>
</article>`;
};

PP.renderFavoritesSkeleton = (count = 3) => {
  const n = Math.max(1, Math.min(count, 6));
  return Array.from({ length: n }, () => `
<article class="card favorites-skeleton" aria-hidden="true">
  <div class="favorites-skeleton-photo"></div>
  <div class="favorites-skeleton-body">
    <div class="favorites-skeleton-line favorites-skeleton-line--wide"></div>
    <div class="favorites-skeleton-line"></div>
    <div class="favorites-skeleton-tags">
      <span></span><span></span>
    </div>
    <div class="favorites-skeleton-actions">
      <span></span><span></span>
    </div>
  </div>
</article>`).join("");
};

PP.renderParentPreview = (p) => {
  const name = p.name || `${p.first_name || ""} ${p.last_name || ""}`.trim() || "Ваше ім'я";
  const photo = p.photo || "";
  const city = p.city || "—";
  const count = p.children_count ?? 0;
  const ages = p.children_ages || "";
  const needs = p.special_needs || "";
  const initial = (name.split(/\s+/)[0]?.[0] || "👤").toUpperCase();
  const agesLine = ages ? ` · вік: ${ages}` : "";
  const needsLine = needs
    ? `<p class="parent-preview-needs">${needs.length > 100 ? `${needs.slice(0, 100)}…` : needs}</p>`
    : "";

  return `
<article class="card parent-preview-card">
  <div class="parent-preview-top">
    <div class="parent-preview-avatar">
      ${photo ? `<img src="${photo}" alt="${name}" width="80" height="80">` : `<span class="parent-preview-fallback">${initial}</span>`}
    </div>
    <div class="parent-preview-info">
      <h3 class="parent-preview-name">${name}</h3>
      <p class="parent-preview-meta">${city}</p>
      ${count > 0 ? `<p class="parent-preview-children">Дітей: ${count}${agesLine}</p>` : ""}
    </div>
  </div>
  ${needsLine}
</article>`;
};

PP.renderNannyListItem = (n) => {
  const url = PP.ROUTES.nanny(n.id);
  const photo = n.photo || "";
  const avatarMarkup = photo
    ? `<img src="${photo}" alt="${n.name}" class="nanny-list-avatar" loading="lazy" width="64" height="64">`
    : `<span class="nanny-list-avatar nanny-list-avatar--fallback" aria-hidden="true">${PP.nannyPhotoInitial(n.name)}</span>`;
  return `
<article class="card nanny-list-item">
  <a href="${url}" class="nanny-list-link">
    ${avatarMarkup}
    <div class="nanny-list-body">
      <p class="nanny-list-name">${n.name}${n.isVerified ? ' <span class="nanny-list-badge">✓</span>' : ""}</p>
      <p class="nanny-list-meta">${n.city}${n.district ? `, ${n.district}` : ""} · ${n.age}\u202fр.</p>
      <div class="nanny-list-tags">
        <span class="nanny-list-tag">${PP.formatPrice(n.hourlyRate)}/год</span>
        <span class="nanny-list-tag">${n.experienceYears}\u202fр. досвіду</span>
      </div>
    </div>
    <div class="nanny-list-aside">
      <span class="nanny-list-rating">${n.rating} ${PP.stars(n.rating)}</span>
      <span class="nanny-list-revcount">${n.reviewCount}\u202fвідг.</span>
      <span class="nanny-list-arrow" aria-hidden="true">›</span>
    </div>
  </a>
  <button type="button" class="nanny-card-fav" data-nanny-id="${n.id}" aria-label="Додати в обране">${PP.favHeartIcon()}</button>
</article>`;
};

PP.renderMiniCalendar = (availability, el, opts = {}) => {
  if (!el) return;
  const months = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"];
  const days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"];
  const start = new Date();
  start.setHours(12, 0, 0, 0);
  const dayCount = opts.days || 14;
  const dateKey = PP.dateKey || ((d) => {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  });
  let html = "";
  if (!opts.hideLegend) {
    html += `
    <div class="calendar-legend">
      <span><span class="legend-dot available"></span>Доступна</span>
      <span><span class="legend-dot busy"></span>Зайнята</span>
    </div>`;
  }
  if (opts.showMonth) {
    html += `<p class="mini-cal-month">${months[start.getMonth()]} ${start.getFullYear()}</p>`;
  }
  html += `<div class="mini-calendar">`;
  days.forEach((d) => { html += `<div class="mini-cal-head">${d}</div>`; });
  const firstDow = (start.getDay() + 6) % 7;
  for (let i = 0; i < firstDow; i++) {
    html += '<div class="mini-cal-day empty"></div>';
  }
  for (let i = 0; i < dayCount; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    const key = dateKey(d);
    const st = availability?.[key] || "available";
    html += `<div class="mini-cal-day ${st}" title="${key}">${d.getDate()}</div>`;
  }
  const totalCells = firstDow + dayCount;
  const remainder = totalCells % 7;
  if (remainder) {
    for (let i = 0; i < 7 - remainder; i++) {
      html += '<div class="mini-cal-day empty"></div>';
    }
  }
  html += "</div>";
  el.innerHTML = html;
};

PP.renderFilters = (container, filters, onChange) => {
  if (!container) return;
  const districts = filters.city ? (PP.DISTRICTS[filters.city] || []) : [];
  const fillPct = (val, min, max) => `${((val - min) / (max - min)) * 100}%`;
  container.innerHTML = `
    <div class="filter-section-head">Місцезнаходження</div>
    <div class="filter-group">
      <label class="label">Місто</label>
      <select class="field" data-f="city">
        <option value="">Усі міста</option>
        ${PP.CITIES.map((c) => `<option value="${c}" ${filters.city === c ? "selected" : ""}>${c}</option>`).join("")}
      </select>
    </div>
    ${districts.length ? `<div class="filter-group"><label class="label">Район</label>
      <select class="field" data-f="district">
        <option value="">Усі</option>
        ${districts.map((d) => `<option value="${d}" ${filters.district === d ? "selected" : ""}>${d}</option>`).join("")}
      </select></div>` : ""}
    <div class="filter-section-head">Параметри</div>
    <div class="filter-params-grid">
      <div class="filter-group">
        <div class="filter-value-row"><span class="label">Вік няні</span><span class="filter-value-badge">від <span data-out="nannyAgeMin">${filters.nannyAgeMin}</span> р.</span></div>
        <input type="range" class="filter-range" data-f="nannyAgeMin" min="18" max="70" value="${filters.nannyAgeMin}" style="--fill:${fillPct(filters.nannyAgeMin,18,70)}">
      </div>
      <div class="filter-group">
        <div class="filter-value-row"><span class="label">Досвід</span><span class="filter-value-badge">від <span data-out="experienceMin">${filters.experienceMin}</span> р.</span></div>
        <input type="range" class="filter-range" data-f="experienceMin" min="0" max="15" value="${filters.experienceMin}" style="--fill:${fillPct(filters.experienceMin,0,15)}">
      </div>
      <div class="filter-group">
        <div class="filter-value-row"><span class="label">Ставка</span><span class="filter-value-badge">до <span data-out="hourlyRateMax">${filters.hourlyRateMax}</span> ₴</span></div>
        <input type="range" class="filter-range" data-f="hourlyRateMax" min="100" max="800" step="50" value="${filters.hourlyRateMax}" style="--fill:${fillPct(filters.hourlyRateMax,100,800)}">
      </div>
      <div class="filter-group">
        <div class="filter-value-row"><span class="label">Рейтинг</span><span class="filter-value-badge">від <span data-out="ratingMin">${filters.ratingMin}</span> ★</span></div>
        <input type="range" class="filter-range" data-f="ratingMin" min="0" max="5" step="0.5" value="${filters.ratingMin}" style="--fill:${fillPct(filters.ratingMin,0,5)}">
      </div>
    </div>
    <div class="filter-section-head">Мова</div>
    <div class="filter-group">
      <div class="lang-pills">
        ${PP.LANGUAGES.map((l) => `<button type="button" class="lang-pill ${filters.languages.includes(l) ? "active" : ""}" data-lang="${l}">${l}</button>`).join("")}
      </div>
    </div>
    <div class="filter-section-head">Бонуси</div>
    <div class="filter-group">
      <div class="filter-check-list">
        <label class="filter-check"><input type="checkbox" data-f="hasCar" ${filters.hasCar ? "checked" : ""}><span>Має автомобіль</span></label>
        <label class="filter-check"><input type="checkbox" data-f="medicalEducation" ${filters.medicalEducation ? "checked" : ""}><span>Медична освіта</span></label>
        <label class="filter-check"><input type="checkbox" data-f="firstAidCourse" ${filters.firstAidCourse ? "checked" : ""}><span>Курс першої допомоги</span></label>
      </div>
    </div>`;

  container.querySelectorAll("[data-f]").forEach((el) => {
    el.addEventListener("input", () => {
      const f = el.dataset.f;
      let val = el.type === "checkbox" ? el.checked : el.type === "range" ? Number(el.value) : el.value;
      if (el.type === "range") {
        const pct = ((val - Number(el.min)) / (Number(el.max) - Number(el.min))) * 100;
        el.style.setProperty("--fill", `${pct}%`);
      }
      if (f === "city") {
        filters.district = "";
        filters.city = val;
        onChange(filters);
        PP.renderFilters(container, filters, onChange);
        return;
      }
      filters[f] = val;
      const out = container.querySelector(`[data-out="${f}"]`);
      if (out) out.textContent = val;
      onChange(filters);
    });
  });

  container.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const l = btn.dataset.lang;
      const i = filters.languages.indexOf(l);
      if (i >= 0) filters.languages.splice(i, 1); else filters.languages.push(l);
      btn.classList.toggle("active");
      onChange(filters);
    });
  });
};

PP.filterNannies = (filters) => PP.NANNIES.filter((n) => {
  if (filters.city && n.city !== filters.city) return false;
  if (filters.district && n.district !== filters.district) return false;
  if (n.age < filters.nannyAgeMin) return false;
  if (n.experienceYears < filters.experienceMin) return false;
  if (n.hourlyRate > filters.hourlyRateMax) return false;
  if (n.rating < filters.ratingMin) return false;
  if (filters.hasCar && !n.hasCar) return false;
  if (filters.medicalEducation && !n.medicalEducation) return false;
  if (filters.firstAidCourse && !n.firstAidCourse) return false;
  if (filters.languages.length && !filters.languages.some((l) => n.languages.includes(l))) return false;
  return true;
});

PP.defaultFilters = () => ({
  city: "", district: "", nannyAgeMin: 18, experienceMin: 0,
  hourlyRateMax: 800, ratingMin: 0, hasCar: false, medicalEducation: false,
  firstAidCourse: false, languages: [],
});

PP.renderCabinetNav = (nav, active) => {
  const norm = PP.normalizePath(active);
  let bestHref = null;
  let bestLen = -1;
  nav.forEach((item) => {
    const hrefNorm = PP.normalizePath(item.href);
    const matches = norm === hrefNorm || norm.startsWith(hrefNorm + "/");
    if (matches && hrefNorm.length > bestLen) {
      bestHref = hrefNorm;
      bestLen = hrefNorm.length;
    }
  });
  return nav.map((item) => {
    const hrefNorm = PP.normalizePath(item.href);
    const isActive = hrefNorm === bestHref;
    return `<a href="${item.href}" class="cabinet-nav-link ${isActive ? "active" : ""}">${item.icon} ${item.label}</a>`;
  }).join("");
};

PP.renderMobileNav = (nav, active) => {
  const norm = PP.normalizePath(active);
  let bestHref = null;
  let bestLen = -1;
  nav.forEach((item) => {
    const hrefNorm = PP.normalizePath(item.href);
    const matches = norm === hrefNorm || norm.startsWith(hrefNorm + "/");
    if (matches && hrefNorm.length > bestLen) {
      bestHref = hrefNorm;
      bestLen = hrefNorm.length;
    }
  });
  return nav.map((item) => {
    const hrefNorm = PP.normalizePath(item.href);
    const isActive = hrefNorm === bestHref;
    return `<a href="${item.href}" class="cabinet-mobile-link ${isActive ? "active" : ""}">${item.label}</a>`;
  }).join("");
};
