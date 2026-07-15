/* Admin cabinet pages */
window.PP = window.PP || {};

PP._roleLabel = (role) =>
  ({ parent: "Батьки", nanny: "Няня", admin: "Адмін" }[role] || role);

PP._statusLabel = (status) =>
  ({ active: "Активний", pending: "Очікує", blocked: "Заблокований" }[status] || status);

PP._modStatusLabel = (status) =>
  ({
    pending: "На модерації",
    approved: "Схвалено",
    rejected: "Відхилено",
    draft: "Чернетка",
  }[status] || status);

PP._paymentStatusLabel = (status) =>
  ({ pending: "Очікує", paid: "Оплачено", failed: "Помилка", refunded: "Повернено" }[status] || status);

PP.djangoAdminUrl = (path = "") => {
  const base = (PP.API_BASE || "").replace(/\/api\/v1\/?$/, "");
  const suffix = path ? path.replace(/^\//, "") : "";
  return `${base}/admin/${suffix}`;
};

PP.openDjangoAdmin = async (path = "", target = "_blank") => {
  const nextPath = path ? `/admin/${path.replace(/^\//, "")}` : "/admin/";
  try {
    const data = await PP.apiFetch("/auth/admin-bridge/", {
      method: "POST",
      body: JSON.stringify({ next: nextPath }),
    });
    if (!data?.url) throw new Error("Не вдалося отримати посилання");
    if (target === "_blank") window.open(data.url, "_blank", "noopener");
    else location.href = data.url;
  } catch (err) {
    alert(err.message || "Не вдалося відкрити Django admin");
  }
};

PP._bindDjangoAdminLinks = (map) => {
  Object.entries(map).forEach(([id, path]) => {
    const el = document.getElementById(id);
    if (!el || el.dataset.djangoSsoBound) return;
    el.dataset.djangoSsoBound = "1";
    el.href = "#";
    el.addEventListener("click", (e) => {
      e.preventDefault();
      PP.openDjangoAdmin(path);
    });
  });
};

PP.initAdminLinks = () => {
  PP._bindDjangoAdminLinks({
    "django-admin-link": "",
    "django-content-pages": "content/staticpage/",
    "django-content-faq": "content/faqitem/",
    "django-content-blog": "content/blogpost/",
    "django-content-settings": "core/sitesettings/",
  });
};

PP.initAdminDashboard = async () => {
  PP.initAdminLinks();
  try {
    const d = await PP.adminDashboard();
    const set = (key, val) => {
      const el = document.querySelector(`[data-stat="${key}"]`);
      if (el) el.textContent = val;
    };
    set("users", d.users_total ?? "—");
    set("nannies", d.nannies_total ?? "—");
    set("revenue", `₴${(d.revenue_uah || 0).toLocaleString("uk-UA")}`);
    set("payments", d.payments_count ?? "0");

    const alerts = document.getElementById("admin-alerts");
    if (alerts) {
      const items = [];
      if (d.pending_profiles > 0) {
        items.push(
          `<a href="/admin/profiles" class="admin-alert admin-alert--warn">${d.pending_profiles} профілів на модерації</a>`
        );
      }
      if (d.pending_documents > 0) {
        items.push(
          `<a href="/admin/documents" class="admin-alert admin-alert--warn">${d.pending_documents} документів очікують</a>`
        );
      }
      if (d.pending_users > 0) {
        items.push(
          `<a href="/admin/users?status=pending" class="admin-alert">${d.pending_users} користувачів очікують</a>`
        );
      }
      alerts.innerHTML = items.join("") || '<p class="admin-alert admin-alert--ok">Немає термінових задач</p>';
    }
  } catch (e) {
    console.warn(e);
  }
};

PP._adminStatusBadge = (status, type = "user") => {
  const cls =
    status === "active" || status === "approved" || status === "paid"
      ? "active"
      : status === "blocked" || status === "rejected" || status === "failed"
        ? "blocked"
        : "pending";
  const label =
    type === "mod" ? PP._modStatusLabel(status) : type === "pay" ? PP._paymentStatusLabel(status) : PP._statusLabel(status);
  return `<span class="admin-badge admin-badge-${cls}">${label}</span>`;
};

PP.initAdminUsers = async () => {
  const tbody = document.querySelector(".admin-table tbody");
  if (!tbody) return;
  const roleEl = document.getElementById("users-filter-role");
  const statusEl = document.getElementById("users-filter-status");
  const params = new URLSearchParams(location.search);
  if (params.get("status") && statusEl) statusEl.value = params.get("status");

  const load = async () => {
    const q = new URLSearchParams();
    if (roleEl?.value) q.set("role", roleEl.value);
    if (statusEl?.value) q.set("status", statusEl.value);
    try {
      const users = await PP.adminUsers(q.toString());
      tbody.innerHTML = users.length
        ? users
            .map(
              (u) => `<tr>
          <td data-label="Email">${u.email}</td>
          <td data-label="Роль">${PP._roleLabel(u.role)}</td>
          <td data-label="Статус">${PP._adminStatusBadge(u.status)}</td>
          <td data-label="Дії">
            <button type="button" class="admin-action-btn" data-id="${u.id}" data-action="${u.status === "blocked" ? "active" : "blocked"}">${u.status === "blocked" ? "Активувати" : "Блокувати"}</button>
            ${u.status === "pending" ? `<button type="button" class="admin-action-btn admin-action-btn--ok" data-id="${u.id}" data-action="active">Активувати</button>` : ""}
          </td>
        </tr>`
            )
            .join("")
        : '<tr><td colspan="4" class="admin-empty">Користувачів не знайдено</td></tr>';
      tbody.querySelectorAll(".admin-action-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
          try {
            await PP.adminUserStatus(Number(btn.dataset.id), btn.dataset.action);
            PP.showToast("Статус оновлено");
            load();
          } catch (err) {
            PP.showToast(err.message, "error");
          }
        });
      });
    } catch (e) {
      console.warn(e);
    }
  };
  roleEl?.addEventListener("change", load);
  statusEl?.addEventListener("change", load);
  load();
};

PP.initAdminProfiles = async () => {
  const tbody = document.querySelector(".admin-table tbody");
  if (!tbody) return;
  const statusEl = document.getElementById("profiles-filter-status");

  const load = async () => {
    const status = statusEl?.value || "pending";
    try {
      const profiles = await PP.adminProfiles(status);
      tbody.innerHTML = profiles.length
        ? profiles
            .map(
              (p) => `<tr>
          <td data-label="Няня"><strong>${p.name}</strong></td>
          <td data-label="Email">${p.email || "—"}</td>
          <td data-label="Місто">${p.city}</td>
          <td data-label="Ставка">${p.hourly_rate ? p.hourly_rate + " ₴/год" : "—"}</td>
          <td data-label="Статус">${PP._adminStatusBadge(p.status, "mod")}</td>
          <td data-label="Дії">
            ${p.status === "pending" ? `<button type="button" class="admin-action-btn admin-action-btn--ok" data-id="${p.id}" data-action="approve">Схвалити</button>
            <button type="button" class="admin-action-btn" data-id="${p.id}" data-action="reject">Відхилити</button>` : "—"}
          </td>
        </tr>`
            )
            .join("")
        : '<tr><td colspan="6" class="admin-empty">Профілів не знайдено</td></tr>';
      tbody.querySelectorAll(".admin-action-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
          try {
            await PP.adminModerateProfile(Number(btn.dataset.id), btn.dataset.action);
            PP.showToast("Профіль оновлено");
            load();
          } catch (err) {
            PP.showToast(err.message, "error");
          }
        });
      });
    } catch (e) {
      console.warn(e);
    }
  };
  statusEl?.addEventListener("change", load);
  load();
};

PP.initAdminDocuments = async () => {
  const tbody = document.querySelector(".admin-table tbody");
  if (!tbody) return;
  const statusEl = document.getElementById("docs-filter-status");

  const load = async () => {
    const status = statusEl?.value || "pending";
    try {
      const docs = await PP.adminDocuments(status);
      tbody.innerHTML = docs.length
        ? docs
            .map(
              (d) => `<tr>
          <td data-label="Няня"><strong>${d.nanny_name}</strong><br><small>${d.email}</small></td>
          <td data-label="Тип">${d.doc_type_label}</td>
          <td data-label="Файл">${d.file_url ? `<a href="${PP.resolveMediaUrl(d.file_url)}" target="_blank" rel="noopener" class="admin-link">Відкрити</a>` : "—"}</td>
          <td data-label="Дата">${new Date(d.uploaded_at).toLocaleDateString("uk-UA")}</td>
          <td data-label="Дії">
            ${d.status === "pending" ? `<button type="button" class="admin-action-btn admin-action-btn--ok" data-id="${d.id}" data-action="approve">OK</button>
            <button type="button" class="admin-action-btn" data-id="${d.id}" data-action="reject">Відхилити</button>` : PP._adminStatusBadge(d.status, "mod")}
          </td>
        </tr>`
            )
            .join("")
        : '<tr><td colspan="5" class="admin-empty">Документів не знайдено</td></tr>';
      tbody.querySelectorAll(".admin-action-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
          try {
            await PP.adminModerateDocument(Number(btn.dataset.id), btn.dataset.action);
            PP.showToast("Документ оновлено");
            load();
          } catch (err) {
            PP.showToast(err.message, "error");
          }
        });
      });
    } catch (e) {
      console.warn(e);
    }
  };
  statusEl?.addEventListener("change", load);
  load();
};

PP.initAdminFinance = async () => {
  const tabs = document.querySelectorAll("[data-finance-tab]");
  const panels = {
    payments: document.getElementById("finance-payments"),
    subscriptions: document.getElementById("finance-subscriptions"),
    commissions: document.getElementById("finance-commissions"),
  };

  const renderPayments = async () => {
    const tbody = panels.payments?.querySelector("tbody");
    if (!tbody) return;
    try {
      const payments = await PP.adminPayments("payments");
      tbody.innerHTML = payments.length
        ? payments
            .map(
              (p) => `<tr>
        <td data-label="Order"><code>${p.order_reference}</code></td>
        <td data-label="Email">${p.email}</td>
        <td data-label="Тариф">${p.plan}</td>
        <td data-label="Сума">₴${p.amount_uah.toLocaleString("uk-UA")}</td>
        <td data-label="Провайдер"><span class="gateway-badge gateway-${p.provider}">${p.provider}</span></td>
        <td data-label="Статус">${PP._adminStatusBadge(p.status, "pay")}</td>
        <td data-label="Дата">${new Date(p.created_at).toLocaleDateString("uk-UA")}</td>
      </tr>`
            )
            .join("")
        : '<tr><td colspan="7" class="admin-empty">Платежів поки немає</td></tr>';
    } catch (e) {
      console.warn(e);
    }
  };

  const renderSubscriptions = async () => {
    const tbody = panels.subscriptions?.querySelector("tbody");
    if (!tbody) return;
    try {
      const subs = await PP.adminPayments("subscriptions");
      tbody.innerHTML = subs.length
        ? subs
            .map(
              (s) => `<tr>
        <td data-label="Email">${s.email}</td>
        <td data-label="Тариф">${s.plan}</td>
        <td data-label="Статус">${PP._adminStatusBadge(s.status, "mod")}</td>
        <td data-label="Контакти">${s.contacts_remaining}</td>
        <td data-label="Місто до">${s.city_access_until ? new Date(s.city_access_until).toLocaleDateString("uk-UA") : "—"}</td>
        <td data-label="Початок">${new Date(s.started_at).toLocaleDateString("uk-UA")}</td>
      </tr>`
            )
            .join("")
        : '<tr><td colspan="6" class="admin-empty">Підписок поки немає</td></tr>';
    } catch (e) {
      console.warn(e);
    }
  };

  const renderCommissions = async () => {
    const root = panels.commissions;
    if (!root) return;
    try {
      const data = await PP.adminPayments("commissions");
      root.innerHTML = `
        <div class="admin-commission-summary card">
          <p>Комісія платформи: <strong>${data.rate_percent}%</strong></p>
          <p>Дохід: <strong>₴${(data.revenue_total_uah || 0).toLocaleString("uk-UA")}</strong></p>
          <p>Комісія: <strong>₴${(data.commission_total_uah || 0).toLocaleString("uk-UA")}</strong></p>
        </div>
        <div class="admin-table-wrap card"><table class="admin-table">
          <thead><tr><th>Order</th><th>Email</th><th>Сума</th><th>Комісія</th><th>Дата</th></tr></thead>
          <tbody>${(data.items || [])
            .map(
              (i) => `<tr>
            <td data-label="Order"><code>${i.order_reference}</code></td>
            <td data-label="Email">${i.email}</td>
            <td data-label="Сума">₴${i.amount_uah.toLocaleString("uk-UA")}</td>
            <td data-label="Комісія">₴${i.commission_uah.toLocaleString("uk-UA")}</td>
            <td data-label="Дата">${new Date(i.created_at).toLocaleDateString("uk-UA")}</td>
          </tr>`
            )
            .join("") || '<tr><td colspan="5" class="admin-empty">Немає оплат</td></tr>'}</tbody>
        </table></div>`;
    } catch (e) {
      console.warn(e);
    }
  };

  const load = (tab) => {
    if (tab === "subscriptions") renderSubscriptions();
    else if (tab === "commissions") renderCommissions();
    else renderPayments();
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.toggle("active", t === tab));
      Object.values(panels).forEach((p) => p?.classList.add("hidden"));
      panels[tab.dataset.financeTab]?.classList.remove("hidden");
      load(tab.dataset.financeTab);
    });
  });

  load("payments");
};

PP.initAdminAnalytics = async () => {
  try {
    const data = await PP.adminAnalytics();

    const setKpi = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };
    setKpi("kpi-dau", data.dau ?? "—");
    setKpi("kpi-mau", data.mau ?? "—");
    setKpi("kpi-conversion", data.conversion_percent != null ? `${data.conversion_percent}%` : "—");
    setKpi("kpi-revenue", `₴${(data.months || []).reduce((s, m) => s + (m.revenue || 0), 0).toLocaleString("uk-UA")}`);

    const chart = document.getElementById("admin-revenue-chart");
    if (chart && data.months?.length) {
      const max = Math.max(...data.months.map((m) => m.revenue), 1);
      chart.innerHTML = data.months
        .map(
          (m) =>
            `<div class="admin-chart-col" title="₴${m.revenue.toLocaleString("uk-UA")}">
          <div class="admin-chart-bar trust" style="height:${Math.max(4, (m.revenue / max) * 100)}%"></div>
          <span class="admin-chart-label">${m.label}</span>
        </div>`
        )
        .join("");
    } else if (chart) {
      chart.innerHTML = '<p class="admin-empty">Недостатньо даних</p>';
    }

    const funnel = document.getElementById("admin-funnel");
    if (funnel && data.funnel) {
      const f = data.funnel;
      const steps = [
        ["Користувачі", f.users],
        ["Батьки", f.parents],
        ["Няні", f.nannies],
        ["Перевірені няні", f.verified_nannies],
        ["Оплатили", f.paid_users],
      ];
      const maxF = f.users || 1;
      funnel.innerHTML = steps
        .map(
          ([label, val]) => `<div class="funnel-step">
        <span class="funnel-label">${label}</span>
        <div class="funnel-bar-wrap"><div class="funnel-bar" style="width:${Math.max(8, (val / maxF) * 100)}%"></div></div>
        <strong class="funnel-value">${val}</strong>
      </div>`
        )
        .join("");
    }

    const roles = document.getElementById("admin-roles");
    if (roles && data.roles) {
      roles.innerHTML = data.roles
        .map((r) => `<div class="admin-role-row"><span>${PP._roleLabel(r.role)}</span><strong>${r.count}</strong></div>`)
        .join("");
    }
  } catch (e) {
    console.warn(e);
  }
};

PP.initAdminContent = () => {
  PP.initAdminLinks();
  PP._bindDjangoAdminLinks({
    "django-cms-home": "core/homeherosettings/",
    "django-cms-hero": "core/homeherosettings/",
    "django-cms-header": "core/siteheadersettings/",
    "django-cms-footer": "core/sitefootersettings/",
    "django-cms-benefits": "core/homebenefitssettings/",
    "django-pricing": "payments/pricingplan/",
  });
};
