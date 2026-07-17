/* Nanny cabinet pages */
window.PP = window.PP || {};

PP.initNannyDashboard = async () => {
  try {
    const p = await PP.fetchNannyProfile();
    const cards = document.querySelectorAll(".stat-card .stat-value");
    if (cards[0]) cards[0].textContent = p.rating ?? "—";
    if (cards[1]) cards[1].textContent = p.reviewCount ?? "0";
  } catch (e) {
    console.warn(e);
  }
};

PP.initNannyProfile = async () => {
  const form = document.querySelector(".profile-form");
  if (!form) return;

  const previewRoot = document.getElementById("profile-card-preview");
  let profileData = {};
  let photoControls = null;

  const readFormData = () => {
    const first = form.querySelector('[name="first_name"]')?.value?.trim() || "";
    const last = form.querySelector('[name="last_name"]')?.value?.trim() || "";
    return {
      name: `${first} ${last}`.trim() || "Ваше ім'я",
      city: form.querySelector('[name="city"]')?.value || profileData.city || "",
      district: profileData.district || "",
      age: profileData.age ?? "—",
      hourlyRate: Number(form.querySelector('[name="hourly_rate"]')?.value || profileData.hourlyRate || 0),
      experienceYears: Number(form.querySelector('[name="experience_years"]')?.value || profileData.experienceYears || 0),
      description: form.querySelector('[name="description"]')?.value || "",
      photo: photoControls?.getLivePhotoUrl() || profileData.photo || "",
      rating: profileData.rating ?? 0,
      reviewCount: profileData.reviewCount ?? 0,
      isVerified: profileData.isVerified ?? false,
      certificates: profileData.certificates || [],
      id: profileData.id || "preview",
    };
  };

  const renderPreview = () => {
    if (!previewRoot) return;
    previewRoot.innerHTML = PP.renderNannyCard(PP.normalizeNanny(readFormData()), { compact: true });
  };

  photoControls = PP.bindProfilePhotoControls({
    uploadFn: async (file) => {
      const updated = await PP.uploadNannyPhoto(file);
      profileData = PP.normalizeNanny(updated);
      return profileData;
    },
    deleteFn: async () => {
      const updated = await PP.deleteNannyPhoto();
      profileData = PP.normalizeNanny(updated);
      return profileData;
    },
    getDisplayName: () => readFormData().name,
    onChange: renderPreview,
  });

  try {
    const p = await PP.fetchNannyProfile();
    profileData = PP.normalizeNanny(p);
    const set = (n, v) => {
      const el = form.querySelector(`[name="${n}"]`);
      if (el) el.value = v ?? "";
    };
    set("first_name", p.name?.split(" ")[0] || p.first_name);
    set("last_name", p.name?.split(" ").slice(1).join(" ") || p.last_name);
    set("birth_date", p.birth_date || "");
    set("phone", p.phone || "");
    set("city", p.city);
    set("hourly_rate", p.hourlyRate);
    set("experience_years", p.experienceYears);
    set("families_count", p.families_count ?? p.familiesCount ?? 0);
    set("recommendations", p.recommendations || "");
    set("description", p.description);
    photoControls.setSavedPhoto(profileData.photo || "");
    const phoneEl = form.querySelector('[name="phone"]');
    if (phoneEl && PP.normalizeUaPhone) {
      phoneEl.value = PP.normalizeUaPhone(phoneEl.value || "+380");
      PP.clearFieldError?.(phoneEl);
    }
    renderPreview();
  } catch (e) {
    console.warn(e);
    renderPreview();
  }

  form.addEventListener("input", () => {
    photoControls?.syncChrome?.();
    renderPreview();
  });

  if (form.dataset.bound) return;
  form.dataset.bound = "1";
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (PP.validateFormContacts && !PP.validateFormContacts(form)) return;
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    try {
      const updated = await PP.saveNannyProfile({
        first_name: form.querySelector('[name="first_name"]')?.value,
        last_name: form.querySelector('[name="last_name"]')?.value,
        birth_date: form.querySelector('[name="birth_date"]')?.value || null,
        phone: form.querySelector('[name="phone"]')?.value,
        description: form.querySelector('[name="description"]')?.value,
        hourly_rate: Number(form.querySelector('[name="hourly_rate"]')?.value || 300),
        experience_years: Number(form.querySelector('[name="experience_years"]')?.value || 0),
        families_count: Number(form.querySelector('[name="families_count"]')?.value || 0),
        recommendations: form.querySelector('[name="recommendations"]')?.value || "",
      });
      profileData = PP.normalizeNanny(updated);
      if (profileData.photo) photoControls.setSavedPhoto(profileData.photo);
      renderPreview();
      PP.showToast("Профіль на модерації");
    } catch (err) {
      alert(err.message);
    } finally {
      btn.disabled = false;
    }
  });
};

PP.initNannyCalendar = async () => {
  const root = document.getElementById("full-calendar");
  if (!root) return;
  let map = {};
  try {
    map = PP.parseAvailabilitySlots(await PP.fetchAvailability());
  } catch (err) {
    console.warn(err);
    PP.showToast("Не вдалося завантажити календар", "error");
  }
  const calendar = PP.initFullCalendar(root, map, true);
  const saveBtn = document.getElementById("cal-save-btn");
  if (!saveBtn || saveBtn.dataset.bound) return;
  saveBtn.dataset.bound = "1";
  saveBtn.addEventListener("click", async () => {
    if (!calendar) return;
    const payload = calendar.getPayload();
    if (!payload.length) {
      PP.showToast("Спочатку позначте дні в календарі", "error");
      return;
    }
    saveBtn.disabled = true;
    try {
      const saved = await PP.saveAvailability(payload);
      calendar.setState(PP.parseAvailabilitySlots(saved));
      PP.showToast("Календар збережено");
    } catch (err) {
      alert(err.message || "Не вдалося зберегти календар");
    } finally {
      saveBtn.disabled = false;
    }
  });
};

PP.initNannyDocuments = async () => {
  const list = document.getElementById("doc-list");
  const form = document.getElementById("doc-upload-form");
  if (!list) return;

  const render = (docs) => {
    const uploaded = {};
    (docs.results || docs).forEach((d) => {
      uploaded[d.doc_type] = d;
    });
    list.innerHTML = Object.entries(PP.DOC_TYPES)
      .filter(([type]) => type !== "criminal_record" || uploaded[type])
      .map(([type, label]) => {
        const doc = uploaded[type];
        const required = PP.REQUIRED_NANNY_DOCS.includes(type) ? ' <span class="doc-required">*</span>' : "";
        return `<div class="doc-row">
          <span class="doc-row-label">${label}${required}</span>
          ${doc ? PP.docStatusBadge(doc.status) : '<span class="badge badge-trust">Не завантажено</span>'}
        </div>`;
      })
      .join("");
  };

  try {
    render(await PP.fetchDocuments());
  } catch (e) {
    console.warn(e);
  }

  if (form) {
    const fileInput = form.querySelector('[name="file"]');
    const fileWrap = document.getElementById("doc-file-wrap");
    const fileNameEl = document.getElementById("doc-file-name");
    const fileSelectedEl = document.getElementById("doc-file-selected");
    const labelTextEl = form.querySelector(".doc-file-label-text");

    const formatFileSize = (bytes) => {
      if (bytes < 1024) return `${bytes} Б`;
      if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} КБ`;
      return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
    };

    const resetFileUi = () => {
      fileWrap?.classList.remove("has-file");
      if (labelTextEl) labelTextEl.textContent = "Обрати файл (PDF, JPG, PNG)";
      if (fileNameEl) fileNameEl.textContent = "";
      fileSelectedEl?.setAttribute("hidden", "");
    };

    const showSelectedFile = (file) => {
      fileWrap?.classList.add("has-file");
      if (labelTextEl) labelTextEl.textContent = "Змінити файл";
      if (fileNameEl) {
        fileNameEl.textContent = `${file.name} · ${formatFileSize(file.size)}`;
      }
      fileSelectedEl?.removeAttribute("hidden");
    };

    fileInput?.addEventListener("change", () => {
      const file = fileInput.files?.[0];
      if (file) showSelectedFile(file);
      else resetFileUi();
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const type = form.querySelector('[name="doc_type"]')?.value;
      const file = fileInput?.files?.[0];
      if (!type || !file) {
        PP.showToast("Оберіть тип документа та файл", "error");
        return;
      }
      const btn = form.querySelector('[type="submit"]');
      const docLabel = PP.DOC_TYPES[type] || type;
      btn.disabled = true;
      try {
        await PP.uploadDocument(type, file);
        PP.showToast(`«${docLabel}» успішно завантажено. Документ надіслано на перевірку.`, "success");
        form.reset();
        resetFileUi();
        render(await PP.fetchDocuments());
      } catch (err) {
        PP.showToast(err.message || "Не вдалося завантажити файл", "error");
      } finally {
        btn.disabled = false;
      }
    });
  }

  if (new URLSearchParams(location.search).get("onboarding")) {
    PP.showToast("Завантажте паспорт та ІПН для перевірки");
  }
};

PP.initNannyRating = async () => {
  const root = document.getElementById("my-reviews");
  if (!root) return;
  try {
    const me = await PP.fetchNannyProfile();
    const avgEl = document.getElementById("rating-avg");
    const countEl = document.getElementById("rating-count");
    const ordersEl = document.getElementById("rating-orders");
    if (avgEl) avgEl.textContent = me.rating ?? "—";
    if (countEl) countEl.textContent = me.reviewCount ?? me.review_count ?? "0";
    if (ordersEl) ordersEl.textContent = me.completedOrders ?? me.completed_orders ?? "0";
    const reviews = await PP.fetchNannyReviews(me.id);
    const list = reviews.results || reviews;
    root.innerHTML = list.length
      ? list
          .map(
            (r) =>
              `<div class="card review-item"><div class="review-item-header"><strong>${r.author}</strong>${PP.stars(r.rating)}</div><p class="review-text">${r.text}</p></div>`
          )
          .join("")
      : '<div class="card empty-state"><p>Ще немає відгуків</p></div>';
  } catch (e) {
    console.warn(e);
  }
};
