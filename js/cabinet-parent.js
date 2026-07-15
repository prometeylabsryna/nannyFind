/* Parent cabinet pages */
window.PP = window.PP || {};

PP.refreshFavoritesCount = async () => {
  try {
    const favs = await PP.fetchFavorites();
    const el = document.querySelectorAll(".stat-card .stat-value")[0];
    if (el) el.textContent = favs.length;
  } catch {
    // silent
  }
};

PP.initParentDashboard = async () => {
  const grid = document.getElementById("dash-nannies");
  try {
    const [favs, subs] = await Promise.all([PP.fetchFavorites(), PP.fetchSubscriptions()]);
    document.querySelectorAll(".stat-card .stat-value")[0].textContent = favs.length;
    document.querySelectorAll(".stat-card .stat-value")[2].textContent =
      subs[0]?.contacts_remaining ?? "0";
    document.querySelectorAll(".stat-card .stat-value")[3].textContent =
      subs[0]?.plan?.title ?? "—";
    if (grid) {
      const list = await PP.fetchNannies({});
      grid.innerHTML = list.slice(0, 6).map((n) => PP.renderNannyListItem(PP.normalizeNanny(n))).join("");
      PP.syncFavoriteButtons?.(grid);
    }
  } catch (e) {
    console.warn(e);
  }
};

PP.initParentProfile = async () => {
  const form = document.querySelector(".profile-form");
  if (!form) return;

  const previewRoot = document.getElementById("profile-card-preview");
  let profileData = {};
  let photoControls = null;

  const readFormData = () => {
    const first = form.querySelector('[name="first_name"]')?.value?.trim() || "";
    const last = form.querySelector('[name="last_name"]')?.value?.trim() || "";
    return {
      first_name: first,
      last_name: last,
      name: `${first} ${last}`.trim() || "Ваше ім'я",
      city: form.querySelector('[name="city"]')?.value || profileData.city || "",
      children_count: Number(form.querySelector('[name="children_count"]')?.value || profileData.children_count || 0),
      children_ages: form.querySelector('[name="children_ages"]')?.value || "",
      special_needs: form.querySelector('[name="special_needs"]')?.value || "",
      photo: photoControls?.getLivePhotoUrl() || profileData.photo || "",
    };
  };

  const renderPreview = () => {
    if (!previewRoot) return;
    previewRoot.innerHTML = PP.renderParentPreview(PP.normalizeParent(readFormData()));
  };

  photoControls = PP.bindProfilePhotoControls({
    uploadFn: async (file) => {
      const updated = await PP.uploadParentPhoto(file);
      profileData = PP.normalizeParent(updated);
      return profileData;
    },
    deleteFn: async () => {
      const updated = await PP.deleteParentPhoto();
      profileData = PP.normalizeParent(updated);
      return profileData;
    },
    getDisplayName: () => readFormData().name,
    onChange: renderPreview,
  });

  try {
    const p = await PP.fetchParentProfile();
    profileData = PP.normalizeParent(p);
    const set = (n, v) => {
      const el = form.querySelector(`[name="${n}"]`);
      if (el) el.value = v ?? "";
    };
    set("first_name", p.first_name);
    set("last_name", p.last_name);
    set("birth_date", p.birth_date || "");
    set("phone", p.phone || "");
    set("city", p.city);
    set("children_count", p.children_count);
    set("children_ages", p.children_ages);
    set("special_needs", p.special_needs);
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
      const updated = await PP.saveParentProfile({
        first_name: form.querySelector('[name="first_name"]')?.value,
        last_name: form.querySelector('[name="last_name"]')?.value,
        birth_date: form.querySelector('[name="birth_date"]')?.value || null,
        phone: form.querySelector('[name="phone"]')?.value,
        children_count: Number(form.querySelector('[name="children_count"]')?.value || 0),
        children_ages: form.querySelector('[name="children_ages"]')?.value,
        special_needs: form.querySelector('[name="special_needs"]')?.value,
      });
      profileData = PP.normalizeParent(updated);
      if (profileData.photo) photoControls.setSavedPhoto(profileData.photo);
      renderPreview();
      PP.showToast("Профіль збережено");
    } catch (err) {
      alert(err.message);
    } finally {
      btn.disabled = false;
    }
  });
};

PP.initParentFavorites = async () => {
  const grid = document.getElementById("fav-grid");
  const toolbar = document.getElementById("favorites-toolbar");
  const countEl = document.getElementById("favorites-count");
  if (!grid) return;

  const pluralNannies = (n) => {
    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) return "няня в обраному";
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "няні в обраному";
    return "нянь в обраному";
  };

  const updateToolbar = (count) => {
    if (!toolbar || !countEl) return;
    if (count > 0) {
      toolbar.hidden = false;
      countEl.innerHTML = `<strong>${count}</strong> ${pluralNannies(count)}`;
    } else {
      toolbar.hidden = true;
      countEl.textContent = "";
    }
  };

  const renderEmpty = () => {
    grid.classList.remove("is-loading");
    grid.setAttribute("aria-busy", "false");
    grid.innerHTML = `
      <div class="favorites-empty card">
        <div class="favorites-empty-icon" aria-hidden="true">♡</div>
        <h2 class="favorites-empty-title">Поки що порожньо</h2>
        <p class="favorites-empty-text">Додавайте нянь у обране з каталогу — так зручніше порівнювати профілі та повертатися до них пізніше.</p>
        <a href="/cabinet/parent/search" class="btn btn-primary">Перейти до пошуку</a>
      </div>`;
    updateToolbar(0);
  };

  const renderError = () => {
    grid.classList.remove("is-loading");
    grid.setAttribute("aria-busy", "false");
    grid.innerHTML = `
      <div class="favorites-empty card favorites-empty--error">
        <div class="favorites-empty-icon" aria-hidden="true">!</div>
        <h2 class="favorites-empty-title">Не вдалось завантажити</h2>
        <p class="favorites-empty-text">Перевірте зʼєднання та спробуйте ще раз.</p>
        <button type="button" class="btn btn-secondary" id="favorites-retry">Спробувати знову</button>
      </div>`;
    document.getElementById("favorites-retry")?.addEventListener("click", () => {
      grid.setAttribute("aria-busy", "true");
      grid.classList.add("is-loading");
      grid.innerHTML = PP.renderFavoritesSkeleton(3);
      loadFavorites();
    });
    updateToolbar(0);
  };

  const renderCards = (favs) => {
    grid.classList.remove("is-loading");
    grid.setAttribute("aria-busy", "false");
    if (!favs.length) {
      renderEmpty();
      return;
    }
    grid.innerHTML = favs.map((f) => PP.renderNannyCard(PP.normalizeNanny(f.nanny), { compact: true })).join("");
    PP.bindChatOpenButtons?.(grid);
    PP.syncFavoriteButtons?.(grid);
    updateToolbar(favs.length);
  };

  const loadFavorites = async () => {
    try {
      const favs = await PP.fetchFavorites();
      renderCards(favs);
    } catch (e) {
      console.warn(e);
      renderError();
    }
  };

  if (!grid.dataset.favPageInit) {
    grid.dataset.favPageInit = "1";
    document.addEventListener("pp:favorite-changed", (e) => {
      if (!e.detail || e.detail.active) return;
      const card = grid.querySelector(`[data-nanny-id="${e.detail.nannyId}"]`)?.closest(".nanny-card");
      if (!card) return;
      card.classList.add("is-removing");
      window.setTimeout(() => {
        card.remove();
        const remaining = grid.querySelectorAll(".nanny-card").length;
        if (remaining === 0) renderEmpty();
        else updateToolbar(remaining);
        PP.refreshFavoritesCount?.();
      }, 280);
    });
  }

  grid.classList.add("is-loading");
  grid.innerHTML = PP.renderFavoritesSkeleton(3);
  await loadFavorites();
};

PP.initParentPayments = async () => {
  const grid = document.getElementById("pay-grid");
  const providerEl = document.getElementById("pay-provider-picker");
  const subEl = document.getElementById("pay-subscription");
  const pendingEl = document.getElementById("pay-pending");
  if (!grid) return;

  const params = new URLSearchParams(location.search);

  if (params.get("stub") && params.get("order")) {
    try {
      await PP.confirmStubPayment(params.get("order"));
      PP.showToast("Оплату підтверджено (stub)");
      history.replaceState({}, "", location.pathname);
    } catch (e) {
      console.warn(e);
    }
  }

  if (params.get("success") === "1") {
    if (pendingEl) {
      pendingEl.hidden = false;
      pendingEl.textContent = "Перевіряємо оплату…";
    }
    try {
      const sub = await PP.waitForActiveSubscription(90000, 2500);
      if (sub) {
        PP.showToast("Підписку активовано");
      } else if (pendingEl) {
        pendingEl.textContent =
          "Оплата ще обробляється. Якщо кошти списано — оновіть сторінку через хвилину.";
      }
    } catch (e) {
      console.warn(e);
    } finally {
      history.replaceState({}, "", location.pathname);
    }
  }

  let providers = [{ code: "stub", label: "Тестовий режим", default: true }];
  let subs = [];
  try {
    const [provData, subData] = await Promise.all([
      PP.fetchPaymentProviders(),
      PP.fetchSubscriptions().catch(() => []),
    ]);
    providers = provData.providers || providers;
    subs = subData || [];
    PP.renderSubscriptionBanner(subEl, subs);
  } catch (e) {
    console.warn(e);
  }

  PP.renderProviderPicker(providerEl, providers);

  try {
    const plans = await PP.fetchPricing();
    grid.innerHTML = plans
      .map(
        (p) => `
      <div class="card pricing-card${p.featured ? " featured" : ""}">
        <h3>${p.title}</h3>
        <div class="pricing-price">${PP.formatPrice(p.price)}</div>
        <p class="pricing-desc">${p.desc || ""}</p>
        <button type="button" class="btn btn-primary btn-block" data-plan="${p.id}">Оплатити</button>
      </div>`
      )
      .join("");
    grid.querySelectorAll("[data-plan]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const provider = PP.getSelectedProvider();
        btn.disabled = true;
        try {
          const result = await PP.processCheckout(btn.dataset.plan, provider);
          if (result.success) {
            PP.showToast("Підписку активовано");
            const freshSubs = await PP.fetchSubscriptions();
            PP.renderSubscriptionBanner(subEl, freshSubs);
          }
        } catch (err) {
          alert(err.message || "Помилка оплати");
        } finally {
          btn.disabled = false;
        }
      });
    });
  } catch (e) {
    grid.innerHTML = PP.PRICING.map(
      (p) =>
        `<div class="card pricing-card${p.featured ? " featured" : ""}"><h3>${p.title}</h3><div class="pricing-price">${PP.formatPrice(p.price)}</div></div>`
    ).join("");
  }

  if (pendingEl && params.get("success") !== "1") {
    pendingEl.hidden = true;
  }
};

PP.initParentReviews = async () => {
  const form = document.getElementById("parent-review-form");
  if (!form) return;

  const select = document.getElementById("review-nanny-select");
  const suggestions = document.getElementById("review-suggestions");
  const hintEl = document.getElementById("review-nanny-hint");

  const showReviewSuccess = (nannyName, rating) => {
    const success = document.getElementById("review-success");
    const textEl = document.getElementById("review-success-text");
    const starsEl = document.getElementById("review-success-stars");
    if (!success) return;

    if (textEl) {
      textEl.textContent = nannyName
        ? `Ваш відгук для ${nannyName} успішно надіслано.`
        : "Ваш відгук успішно надіслано.";
    }
    if (starsEl && rating > 0) {
      starsEl.innerHTML = PP.stars(rating);
      starsEl.hidden = false;
    } else if (starsEl) {
      starsEl.hidden = true;
    }

    form.hidden = true;
    if (suggestions) suggestions.hidden = true;
    success.hidden = false;
    success.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  const hideReviewSuccess = () => {
    const success = document.getElementById("review-success");
    if (success) success.hidden = true;
    form.hidden = false;
    form.reset();
    document.querySelectorAll(".review-stars-input button").forEach((s) => s.classList.remove("active"));
    const ratingInput = document.getElementById("rating-input");
    if (ratingInput) ratingInput.value = "0";
    loadReviewData();
  };

  const renderSelect = (reviewable, favorites) => {
    if (!select) return;
    const reviewableIds = new Set((reviewable || []).map((n) => String(n.id)));
    const pending = (favorites || [])
      .map((f) => f.nanny)
      .filter((n) => n && !reviewableIds.has(String(n.id)));

    select.replaceChildren();

    const addOption = (value, text, disabled = false) => {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = text;
      opt.disabled = disabled;
      select.appendChild(opt);
    };

    addOption("", "Оберіть няню");
    (reviewable || []).forEach((n) => {
      addOption(String(n.id), `${n.name} · ${n.city || "—"}`);
    });
    if (pending.length) {
      addOption("", "— З обраного: спочатку відкрийте контакт —", true);
      pending.forEach((n) => {
        addOption("", `${n.name} · ${n.city || "—"}`, true);
      });
    }

    const pre = new URLSearchParams(location.search).get("nanny");
    if (pre && reviewableIds.has(String(pre))) {
      select.value = pre;
      select.dispatchEvent(new Event("change", { bubbles: true }));
    }

    PP.CustomSelect?.refresh?.(select);
  };

  const renderSuggestions = (reviewable, favorites) => {
    if (!suggestions) return;
    const reviewableIds = new Set((reviewable || []).map((n) => String(n.id)));
    const pending = (favorites || [])
      .map((f) => f.nanny)
      .filter((n) => n && !reviewableIds.has(String(n.id)));

    if (!pending.length) {
      suggestions.hidden = true;
      suggestions.innerHTML = "";
      return;
    }

    suggestions.hidden = false;
    suggestions.innerHTML = `
      <h2 class="review-suggestions-title">Няні з обраного</h2>
      <p class="review-suggestions-text">Щоб залишити відгук, відкрийте контакт у профілі няні.</p>
      <div class="review-suggestions-grid">
        ${pending
          .map(
            (n) => `
          <article class="card review-suggestion-card">
            <img src="${n.photo || ""}" alt="" class="review-suggestion-avatar" width="56" height="56" loading="lazy">
            <div class="review-suggestion-body">
              <h3 class="review-suggestion-name">${n.name}</h3>
              <p class="review-suggestion-meta">${n.city || "—"}</p>
            </div>
            <a href="${PP.ROUTES.nanny(n.id)}" class="btn btn-secondary review-suggestion-btn">Відкрити профіль</a>
          </article>`
          )
          .join("")}
      </div>`;
  };

  const updateHint = (reviewable, favorites) => {
    if (!hintEl) return;
    const hasReviewable = (reviewable || []).length > 0;
    const hasFavorites = (favorites || []).length > 0;

    if (hasReviewable) {
      hintEl.textContent = "Оберіть няню, з якою вже відкрито контакт.";
      hintEl.hidden = false;
      return;
    }
    if (hasFavorites) {
      hintEl.textContent =
        "У списку видно нянь з обраного. Для відгуку спочатку відкрийте контакт у їхньому профілі.";
      hintEl.hidden = false;
      return;
    }
    hintEl.innerHTML =
      'Немає нянь для відгуку. <a href="/cabinet/parent/search">Знайдіть няню</a> або додайте в <a href="/cabinet/parent/favorites">обране</a>.';
    hintEl.hidden = false;
  };

  const loadReviewData = async () => {
    if (!select) return;
    if (document.getElementById("review-success") && !document.getElementById("review-success").hidden) return;
    try {
      const [reviewableRaw, favorites] = await Promise.all([
        PP.fetchReviewableNannies(),
        PP.fetchFavorites().catch(() => []),
      ]);
      const reviewable = Array.isArray(reviewableRaw) ? reviewableRaw : [];
      renderSelect(reviewable, favorites);
      renderSuggestions(reviewable, favorites);
      updateHint(reviewable, favorites);
    } catch (e) {
      console.warn(e);
      if (hintEl) {
        hintEl.textContent = "Не вдалось завантажити список нянь. Спробуйте оновити сторінку.";
        hintEl.hidden = false;
      }
    }
  };

  if (!form.dataset.reviewInit) {
    form.dataset.reviewInit = "1";
    window.addEventListener("pageshow", () => {
      if (!document.getElementById("review-success")?.hidden) return;
      loadReviewData();
    });
    document.addEventListener("pp:contact-unlocked", () => loadReviewData());
    document.getElementById("review-success-again")?.addEventListener("click", hideReviewSuccess);
  }

  await loadReviewData();

  PP.initReview?.();

  if (form.dataset.bound) return;
  form.dataset.bound = "1";
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const nannyId =
      form.querySelector('[name="nanny_id"]')?.value ||
      select?.value ||
      new URLSearchParams(location.search).get("nanny");
    const rating = Number(document.getElementById("rating-input")?.value || 0);
    const text = form.querySelector("textarea")?.value || "";
    if (!nannyId || !rating) {
      alert("Оберіть няню та оцінку");
      return;
    }
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    const nannyLabel =
      select?.selectedOptions?.[0]?.text?.trim() ||
      select?.querySelector(`option[value="${nannyId}"]`)?.textContent?.trim() ||
      "";
    try {
      await PP.submitReview(Number(nannyId), rating, text);
      showReviewSuccess(nannyLabel.split("·")[0]?.trim() || nannyLabel, rating);
    } catch (err) {
      alert(err.message);
    } finally {
      btn.disabled = false;
    }
  });
};
