/* Full calendar — зелений/червоний/відпустка */
window.PP = window.PP || {};

PP.initFullCalendar = (container, availability, editable) => {
  if (!container) return null;
  let state = { ...availability };
  let activeStatus = "available";
  let selected = null;
  let viewDate = new Date();

  const months = ["Січень","Лютий","Березень","Квітень","Травень","Червень","Липень","Серпень","Вересень","Жовтень","Листопад","Грудень"];

  const dateKey = (y, m, d) =>
    `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;

  const todayKey = () => {
    const now = new Date();
    return dateKey(now.getFullYear(), now.getMonth(), now.getDate());
  };

  function render() {
    const y = viewDate.getFullYear(), m = viewDate.getMonth();
    const first = (new Date(y, m, 1).getDay() + 6) % 7;
    const total = new Date(y, m + 1, 0).getDate();
    const days = ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"];
    const today = todayKey();

    let html = `
      <div class="calendar-legend">
        <span><span class="legend-dot available"></span>Доступна</span>
        <span><span class="legend-dot busy"></span>Зайнята</span>
        <span><span class="legend-dot vacation"></span>Відпустка</span>
      </div>
      <div class="calendar-nav">
        <button type="button" class="calendar-nav-btn" data-nav="-1" aria-label="Попередній місяць">
          <span aria-hidden="true">‹</span>
        </button>
        <h3 class="calendar-nav-title">${months[m]} <span class="calendar-nav-year">${y}</span></h3>
        <button type="button" class="calendar-nav-btn" data-nav="1" aria-label="Наступний місяць">
          <span aria-hidden="true">›</span>
        </button>
      </div>
      <div class="full-calendar">`;
    days.forEach((d, i) => {
      const weekend = i >= 5 ? " weekend" : "";
      html += `<div class="full-cal-head${weekend}">${d}</div>`;
    });
    for (let i = 0; i < first; i++) html += '<div class="full-cal-empty" aria-hidden="true"></div>';
    for (let d = 1; d <= total; d++) {
      const key = dateKey(y, m, d);
      const st = state[key] || "available";
      const isToday = key === today ? " today" : "";
      const isSelected = selected === key ? " selected" : "";
      html += `<button type="button" class="full-cal-day ${st}${isToday}${isSelected}" data-date="${key}" aria-pressed="${selected === key}">${d}</button>`;
    }
    html += "</div>";
    if (editable) {
      html += `<div class="calendar-toolbar" role="group" aria-label="Статус дня">
        <button type="button" class="cal-status-btn available ${activeStatus === "available" ? "active" : ""}" data-st="available" aria-pressed="${activeStatus === "available"}">Доступна</button>
        <button type="button" class="cal-status-btn busy ${activeStatus === "busy" ? "active" : ""}" data-st="busy" aria-pressed="${activeStatus === "busy"}">Зайнята</button>
        <button type="button" class="cal-status-btn vacation ${activeStatus === "vacation" ? "active" : ""}" data-st="vacation" aria-pressed="${activeStatus === "vacation"}">Відпустка</button>
      </div>`;
    }
    container.innerHTML = html;

    container.querySelectorAll("[data-nav]").forEach((btn) => {
      btn.addEventListener("click", () => {
        viewDate.setMonth(viewDate.getMonth() + Number(btn.dataset.nav));
        render();
      });
    });

    container.querySelectorAll("[data-date]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (!editable) return;
        selected = btn.dataset.date;
        state[selected] = activeStatus;
        render();
      });
    });

    container.querySelectorAll("[data-st]").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeStatus = btn.dataset.st;
        if (selected) state[selected] = activeStatus;
        render();
      });
    });
  }

  render();

  return {
    getState: () => ({ ...state }),
    setState: (next) => {
      state = { ...next };
      render();
    },
    getPayload: () =>
      Object.entries(state).map(([date, status]) => ({ date, status })),
  };
};
