/* Datepicker — кастомний calendar для input[type=date].field */
window.PP = window.PP || {};

PP.DatePicker = (() => {
  const MONTHS = [
    "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
    "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень",
  ];
  const MONTHS_SHORT = [
    "січ.", "лют.", "бер.", "квіт.", "трав.", "черв.",
    "лип.", "серп.", "вер.", "жовт.", "лист.", "груд.",
  ];
  const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"];

  const ICON = `<svg class="dp-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="15" rx="2.5" stroke="currentColor" stroke-width="1.5"/><path stroke="currentColor" stroke-width="1.5" stroke-linecap="round" d="M8 3.5v4M16 3.5v4M3.5 10h17"/></svg>`;

  const instances = new WeakMap();
  let openRoot = null;

  const pad = (n) => String(n).padStart(2, "0");
  const toKey = (y, m, d) => `${y}-${pad(m + 1)}-${pad(d)}`;
  const parseKey = (s) => {
    if (!s || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
    const [y, m, d] = s.split("-").map(Number);
    const dt = new Date(y, m - 1, d);
    if (dt.getFullYear() !== y || dt.getMonth() !== m - 1 || dt.getDate() !== d) return null;
    return dt;
  };
  const formatDisplay = (s) => {
    const dt = parseKey(s);
    if (!dt) return "";
    return `${pad(dt.getDate())}.${pad(dt.getMonth() + 1)}.${dt.getFullYear()}`;
  };
  const todayKey = () => {
    const n = new Date();
    return toKey(n.getFullYear(), n.getMonth(), n.getDate());
  };
  const isMobile = () => window.matchMedia("(max-width: 767px)").matches;

  function getBounds(input) {
    let min = parseKey(input.getAttribute("min") || "");
    let max = parseKey(input.getAttribute("max") || "");
    const now = new Date();
    if (input.name === "birth_date") {
      if (!max) max = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      if (!min) min = new Date(now.getFullYear() - 100, 0, 1);
    }
    return {
      min: min || new Date(now.getFullYear() - 100, 0, 1),
      max: max || new Date(now.getFullYear() + 5, 11, 31),
    };
  }

  function inRange(y, m, d, bounds) {
    const t = new Date(y, m, d).setHours(0, 0, 0, 0);
    const minT = new Date(bounds.min.getFullYear(), bounds.min.getMonth(), bounds.min.getDate()).getTime();
    const maxT = new Date(bounds.max.getFullYear(), bounds.max.getMonth(), bounds.max.getDate()).getTime();
    return t >= minT && t <= maxT;
  }

  function build(input) {
    if (input.dataset.dpInit) return;
    input.dataset.dpInit = "1";

    const root = document.createElement("div");
    root.className = "dp-root";

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "dp-trigger";
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.setAttribute("aria-expanded", "false");
    trigger.innerHTML = `<span class="dp-value is-placeholder">Оберіть дату</span>${ICON}`;

    const valueEl = trigger.querySelector(".dp-value");
    if (input.id) {
      trigger.id = `${input.id}-dp`;
      const lbl = document.querySelector(`label[for="${input.id}"]`);
      if (lbl) lbl.setAttribute("for", trigger.id);
    }
    if (input.required) trigger.setAttribute("aria-required", "true");

    const panel = document.createElement("div");
    panel.className = "dp-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "true");
    panel.hidden = true;

    const backdrop = document.createElement("div");
    backdrop.className = "dp-backdrop";
    backdrop.hidden = true;

    input.parentNode.insertBefore(root, input);
    root.appendChild(trigger);
    root.appendChild(panel);
    document.body.appendChild(backdrop);
    root.appendChild(input);

    input.setAttribute("aria-hidden", "true");
    input.tabIndex = -1;
    input.style.cssText =
      "position:absolute;opacity:0;pointer-events:none;width:0;height:0;overflow:hidden;border:0;padding:0;margin:0;";

    const state = {
      view: "days",
      cursor: parseKey(input.value) || new Date(),
      input,
      root,
      trigger,
      panel,
      backdrop,
      valueEl,
    };
    instances.set(input, state);
    syncDisplay(state);

    const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    Object.defineProperty(input, "value", {
      configurable: true,
      get() {
        return desc.get.call(this);
      },
      set(v) {
        desc.set.call(this, v);
        syncDisplay(state);
      },
    });

    trigger.addEventListener("click", (e) => {
      e.stopPropagation();
      state.panel.hidden ? open(state) : close(state);
    });

    trigger.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        close(state);
        return;
      }
      if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
        e.preventDefault();
        if (state.panel.hidden) open(state);
      }
    });

    backdrop.addEventListener("click", () => close(state));

    panel.addEventListener("click", (e) => e.stopPropagation());
  }

  function syncDisplay(state) {
    const raw = state.input.value;
    const text = formatDisplay(raw);
    if (text) {
      state.valueEl.textContent = text;
      state.valueEl.classList.remove("is-placeholder");
    } else {
      state.valueEl.textContent = "Оберіть дату";
      state.valueEl.classList.add("is-placeholder");
    }
  }

  function open(state) {
    if (openRoot && openRoot !== state.root) {
      const other = [...document.querySelectorAll(".dp-root.is-open")];
      other.forEach((r) => {
        const inp = r.querySelector('input[type="date"]');
        const st = inp && instances.get(inp);
        if (st) close(st);
      });
    }

    const parsed = parseKey(state.input.value);
    state.cursor = parsed ? new Date(parsed) : new Date();
    state.view = "days";
    render(state);

    state.panel.hidden = false;
    state.root.classList.add("is-open");
    state.trigger.setAttribute("aria-expanded", "true");
    openRoot = state.root;

    if (isMobile()) {
      state.backdrop.hidden = false;
      requestAnimationFrame(() => state.backdrop.classList.add("is-visible"));
      document.body.style.overflow = "hidden";
    } else {
      state.backdrop.hidden = true;
      state.backdrop.classList.remove("is-visible");
      placePanel(state);
    }
  }

  function close(state) {
    state.panel.hidden = true;
    state.root.classList.remove("is-open");
    state.trigger.setAttribute("aria-expanded", "false");
    state.backdrop.classList.remove("is-visible");
    state.backdrop.hidden = true;
    document.body.style.overflow = "";
    if (openRoot === state.root) openRoot = null;
  }

  function placePanel(state) {
    const rect = state.trigger.getBoundingClientRect();
    const panelH = state.panel.offsetHeight || 320;
    const spaceBelow = window.innerHeight - rect.bottom;
    const openUp = spaceBelow < panelH + 16 && rect.top > spaceBelow;
    state.panel.style.top = openUp ? "auto" : "calc(100% + 0.375rem)";
    state.panel.style.bottom = openUp ? "calc(100% + 0.375rem)" : "auto";
    state.panel.style.left = "0";
    state.panel.style.right = "auto";
  }

  function shiftCursor(state, dir) {
    const c = state.cursor;
    if (state.view === "days") c.setMonth(c.getMonth() + dir);
    else if (state.view === "months") c.setFullYear(c.getFullYear() + dir);
    else c.setFullYear(c.getFullYear() + dir * 12);
    render(state);
  }

  function render(state) {
    const y = state.cursor.getFullYear();
    const m = state.cursor.getMonth();
    const bounds = getBounds(state.input);
    const selected = state.input.value;
    const today = todayKey();

    let title = "";
    if (state.view === "days") title = `${MONTHS[m]} ${y}`;
    else if (state.view === "months") title = String(y);
    else {
      const start = y - (y % 12);
      title = `${start} – ${start + 11}`;
    }

    let body = "";
    if (state.view === "days") {
      body += `<div class="dp-weekdays" aria-hidden="true">`;
      WEEKDAYS.forEach((d, i) => {
        body += `<span class="dp-weekday${i >= 5 ? " is-weekend" : ""}">${d}</span>`;
      });
      body += `</div><div class="dp-grid" role="grid">`;

      const first = (new Date(y, m, 1).getDay() + 6) % 7;
      const total = new Date(y, m + 1, 0).getDate();
      const prevTotal = new Date(y, m, 0).getDate();

      for (let i = 0; i < first; i++) {
        const d = prevTotal - first + i + 1;
        const pm = m === 0 ? 11 : m - 1;
        const py = m === 0 ? y - 1 : y;
        const key = toKey(py, pm, d);
        const disabled = !inRange(py, pm, d, getBounds(state.input));
        body += cellBtn(d, key, {
          outside: true,
          selected: key === selected,
          today: key === today,
          disabled,
        });
      }
      for (let d = 1; d <= total; d++) {
        const key = toKey(y, m, d);
        const disabled = !inRange(y, m, d, bounds);
        body += cellBtn(d, key, {
          selected: key === selected,
          today: key === today,
          disabled,
        });
      }
      const filled = first + total;
      const rest = filled % 7 === 0 ? 0 : 7 - (filled % 7);
      for (let i = 1; i <= rest; i++) {
        const nm = m === 11 ? 0 : m + 1;
        const ny = m === 11 ? y + 1 : y;
        const key = toKey(ny, nm, i);
        const disabled = !inRange(ny, nm, i, getBounds(state.input));
        body += cellBtn(i, key, {
          outside: true,
          selected: key === selected,
          today: key === today,
          disabled,
        });
      }
      body += "</div>";
    } else if (state.view === "months") {
      body += `<div class="dp-grid dp-grid--months" role="grid">`;
      MONTHS_SHORT.forEach((label, i) => {
        const sel = selected && parseKey(selected)?.getFullYear() === y && parseKey(selected)?.getMonth() === i;
        body += `<button type="button" class="dp-cell${sel ? " is-selected" : ""}" data-month="${i}">${label}</button>`;
      });
      body += "</div>";
    } else {
      const start = y - (y % 12);
      body += `<div class="dp-grid dp-grid--years" role="grid">`;
      for (let i = 0; i < 12; i++) {
        const yr = start + i;
        const sel = selected && parseKey(selected)?.getFullYear() === yr;
        const disabled = yr < bounds.min.getFullYear() || yr > bounds.max.getFullYear();
        body += `<button type="button" class="dp-cell${sel ? " is-selected" : ""}" data-year="${yr}" ${disabled ? "disabled" : ""}>${yr}</button>`;
      }
      body += "</div>";
    }

    const showToday = state.input.name !== "birth_date";
    state.panel.innerHTML = `
      <div class="dp-nav">
        <button type="button" class="dp-nav-btn" data-nav="-1" aria-label="Назад"><span aria-hidden="true">‹</span></button>
        <button type="button" class="dp-nav-title" data-title>${title}</button>
        <button type="button" class="dp-nav-btn" data-nav="1" aria-label="Далі"><span aria-hidden="true">›</span></button>
      </div>
      ${body}
      <div class="dp-footer">
        <button type="button" class="dp-footer-btn" data-clear>Очистити</button>
        ${showToday ? '<button type="button" class="dp-footer-btn dp-footer-btn--accent" data-today>Сьогодні</button>' : "<span></span>"}
      </div>
    `;

    bindPanel(state);
    if (!isMobile()) placePanel(state);
  }

  function cellBtn(label, key, { outside, selected, today, disabled } = {}) {
    const cls = [
      "dp-cell",
      outside ? "is-outside" : "",
      selected ? "is-selected" : "",
      today ? "is-today" : "",
    ]
      .filter(Boolean)
      .join(" ");
    return `<button type="button" class="${cls}" data-date="${key}" ${disabled ? "disabled" : ""} aria-pressed="${!!selected}">${label}</button>`;
  }

  function bindPanel(state) {
    state.panel.querySelectorAll("[data-nav]").forEach((btn) => {
      btn.addEventListener("click", () => shiftCursor(state, Number(btn.dataset.nav)));
    });

    state.panel.querySelector("[data-title]")?.addEventListener("click", () => {
      if (state.view === "days") state.view = "months";
      else if (state.view === "months") state.view = "years";
      else state.view = "days";
      render(state);
    });

    state.panel.querySelectorAll("[data-date]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.input.value = btn.dataset.date;
        state.input.dispatchEvent(new Event("input", { bubbles: true }));
        state.input.dispatchEvent(new Event("change", { bubbles: true }));
        syncDisplay(state);
        close(state);
        state.trigger.focus();
      });
    });

    state.panel.querySelectorAll("[data-month]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.cursor.setMonth(Number(btn.dataset.month));
        state.view = "days";
        render(state);
      });
    });

    state.panel.querySelectorAll("[data-year]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.cursor.setFullYear(Number(btn.dataset.year));
        state.view = "months";
        render(state);
      });
    });

    state.panel.querySelector("[data-clear]")?.addEventListener("click", () => {
      state.input.value = "";
      state.input.dispatchEvent(new Event("input", { bubbles: true }));
      state.input.dispatchEvent(new Event("change", { bubbles: true }));
      syncDisplay(state);
      close(state);
      state.trigger.focus();
    });

    state.panel.querySelector("[data-today]")?.addEventListener("click", () => {
      const key = todayKey();
      const bounds = getBounds(state.input);
      const dt = parseKey(key);
      if (!dt || !inRange(dt.getFullYear(), dt.getMonth(), dt.getDate(), bounds)) return;
      state.input.value = key;
      state.input.dispatchEvent(new Event("input", { bubbles: true }));
      state.input.dispatchEvent(new Event("change", { bubbles: true }));
      syncDisplay(state);
      close(state);
      state.trigger.focus();
    });
  }

  function refresh(input) {
    const state = instances.get(input);
    if (!state) return;
    syncDisplay(state);
    if (!state.panel.hidden) {
      state.cursor = parseKey(input.value) || state.cursor;
      render(state);
    }
  }

  function init(container) {
    (container || document)
      .querySelectorAll('input.field[type="date"]:not([data-dp-init])')
      .forEach(build);
  }

  document.addEventListener("click", (e) => {
    if (!openRoot) return;
    if (openRoot.contains(e.target)) return;
    const inp = openRoot.querySelector('input[type="date"]');
    const st = inp && instances.get(inp);
    if (st && !st.backdrop.contains(e.target)) close(st);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || !openRoot) return;
    const inp = openRoot.querySelector('input[type="date"]');
    const st = inp && instances.get(inp);
    if (st) {
      close(st);
      st.trigger.focus();
    }
  });

  window.addEventListener(
    "resize",
    () => {
      if (!openRoot) return;
      const inp = openRoot.querySelector('input[type="date"]');
      const st = inp && instances.get(inp);
      if (!st || st.panel.hidden) return;
      if (isMobile()) {
        st.backdrop.hidden = false;
        st.backdrop.classList.add("is-visible");
        document.body.style.overflow = "hidden";
        st.panel.style.top = "";
        st.panel.style.bottom = "";
      } else {
        st.backdrop.classList.remove("is-visible");
        st.backdrop.hidden = true;
        document.body.style.overflow = "";
        placePanel(st);
      }
    },
    { passive: true }
  );

  document.addEventListener("DOMContentLoaded", () => init());

  return { init, refresh };
})();
