/* Payment checkout helpers — LiqPay, WayForPay, Fondy, stub */
window.PP = window.PP || {};

PP._wfpScriptPromise = null;

PP.loadWayForPayScript = () => {
  if (window.Wayforpay) return Promise.resolve();
  if (PP._wfpScriptPromise) return PP._wfpScriptPromise;
  PP._wfpScriptPromise = new Promise((resolve, reject) => {
    const existing = document.getElementById("wayforpay_script");
    if (existing) {
      existing.addEventListener("load", () => resolve());
      existing.addEventListener("error", reject);
      return;
    }
    const s = document.createElement("script");
    s.id = "wayforpay_script";
    s.src = "https://secure.wayforpay.com/server/pay-widget.js";
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error("Не вдалось завантажити WayForPay"));
    document.head.appendChild(s);
  });
  return PP._wfpScriptPromise;
};

PP.submitLiqPayCheckout = (checkout) => {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = checkout.checkout_url;
  form.acceptCharset = "utf-8";
  form.style.display = "none";
  const dataInput = document.createElement("input");
  dataInput.type = "hidden";
  dataInput.name = "data";
  dataInput.value = checkout.data;
  const sigInput = document.createElement("input");
  sigInput.type = "hidden";
  sigInput.name = "signature";
  sigInput.value = checkout.signature;
  form.append(dataInput, sigInput);
  document.body.appendChild(form);
  form.submit();
};

PP.runWayForPayCheckout = async (checkout) => {
  await PP.loadWayForPayScript();
  if (!window.Wayforpay) throw new Error("WayForPay widget недоступний");
  const wfp = new Wayforpay();
  return new Promise((resolve, reject) => {
    wfp.run({
      merchantAccount: checkout.merchantAccount,
      merchantDomainName: checkout.merchantDomainName,
      merchantSignature: checkout.merchantSignature,
      orderReference: checkout.orderReference,
      orderDate: checkout.orderDate,
      amount: checkout.amount,
      currency: checkout.currency,
      productName: checkout.productName,
      productCount: checkout.productCount,
      productPrice: checkout.productPrice,
      serviceUrl: checkout.serviceUrl,
      returnUrl: checkout.returnUrl,
      language: "UA",
    });
    wfp.onApprove = () => resolve({ approved: true });
    wfp.onDecline = () => reject(new Error("Оплату відхилено"));
    wfp.onPending = () => resolve({ pending: true });
  });
};

PP.processCheckout = async (planCode, provider) => {
  const res = await PP.checkout(planCode, provider);
  const c = res.checkout;
  if (c.stub) {
    await PP.confirmStubPayment(res.payment.order_reference);
    return { success: true, stub: true };
  }
  if (c.provider === "liqpay" && c.data && c.signature) {
    PP.submitLiqPayCheckout(c);
    return { redirect: true };
  }
  if (c.provider === "wayforpay") {
    await PP.runWayForPayCheckout(c);
    return { widget: true };
  }
  if (c.provider === "fondy" && c.checkout_url) {
    window.location.href = c.checkout_url;
    return { redirect: true };
  }
  throw new Error("Невідомий формат checkout від провайдера.");
};

PP.findActiveSubscription = (subs) =>
  (subs || []).find(
    (s) =>
      s.status === "active" &&
      (s.contacts_remaining > 0 || (s.city_access_until && new Date(s.city_access_until) > new Date()))
  );

PP.waitForActiveSubscription = async (timeoutMs = 60000, intervalMs = 2000) => {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const active = PP.findActiveSubscription(await PP.fetchSubscriptions());
    if (active) return active;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return null;
};

PP.renderProviderPicker = (container, providers, selectedCode) => {
  if (!container || !providers?.length) return selectedCode;
  const selectable = providers.filter((p) => p.configured !== false);
  const defaultCode =
    selectedCode || selectable.find((p) => p.default)?.code || selectable[0]?.code || providers[0].code;
  container.innerHTML = `
    <fieldset class="pay-provider-fieldset">
      <legend class="pay-provider-legend">Спосіб оплати</legend>
      <div class="pay-provider-options">
        ${providers
          .map((p) => {
            const disabled = p.configured === false;
            const checked = p.code === defaultCode && !disabled;
            return `
          <label class="pay-provider-option${disabled ? " is-disabled" : ""}">
            <input type="radio" name="pay-provider" value="${p.code}"${checked ? " checked" : ""}${disabled ? " disabled" : ""}>
            <span class="pay-provider-label">${p.label}${disabled ? " (скоро)" : ""}</span>
          </label>`;
          })
          .join("")}
      </div>
      ${providers.some((p) => p.code === "stub" && p.configured) ? '<p class="form-hint">У тестовому режимі оплата проходить без реального списання.</p>' : ""}
    </fieldset>`;
  return defaultCode;
};

PP.getSelectedProvider = () => {
  const checked = document.querySelector('input[name="pay-provider"]:checked:not(:disabled)');
  if (checked?.value) return checked.value;
  const fallback = document.querySelector('input[name="pay-provider"]:not(:disabled)');
  return fallback?.value || "stub";
};

PP.renderSubscriptionBanner = (container, subs) => {
  if (!container) return;
  const active = PP.findActiveSubscription(subs);
  if (!active) {
    container.innerHTML = "";
    container.hidden = true;
    return;
  }
  container.hidden = false;
  const cityUntil = active.city_access_until
    ? new Date(active.city_access_until).toLocaleDateString("uk-UA")
    : null;
  const detail = cityUntil
    ? `Доступ до контактів у вашому місті до ${cityUntil}`
    : `Залишилось контактів: ${active.contacts_remaining}`;
  container.innerHTML = `
    <div class="pay-subscription-inner">
      <div>
        <p class="pay-subscription-title">Активна підписка: ${active.plan?.title || "—"}</p>
        <p class="pay-subscription-meta">${detail}</p>
      </div>
    </div>`;
};

PP._profilePhoneSubscribeHint = () => `
  <span class="profile-phone-hint-text">Щоб переглянути телефон, потрібно купити підписку.</span>
  <a href="${PP.ROUTES.parentPayments}" class="btn btn-secondary btn-block profile-phone-subscribe-btn">Оформити підписку</a>`;

PP._bindProfilePhoneUnlock = (block, nannyId, btn, hint) => {
  if (!btn || !hint) return;
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    hint.classList.remove("profile-phone-hint--error", "profile-phone-hint--ok");
    hint.textContent = "Завантаження…";
    try {
      const res = await PP.unlockContact(Number(nannyId));
      block.innerHTML = `
        <p class="profile-phone-label">Телефон</p>
        <a href="tel:${res.phone.replace(/\s/g, "")}" class="profile-phone-link">${res.phone}</a>`;
      PP.showToast?.("Контакт відкрито");
      document.dispatchEvent(
        new CustomEvent("pp:contact-unlocked", { detail: { nannyId: String(nannyId) } })
      );
    } catch (err) {
      if (err.status === 402) {
        hint.classList.add("profile-phone-hint--error");
        hint.innerHTML = PP._profilePhoneSubscribeHint();
      } else {
        hint.classList.remove("profile-phone-hint--error");
        hint.textContent = err.message || "Помилка";
      }
      btn.disabled = false;
    }
  });
};

PP.initProfilePhone = async (nannyId, phoneFromApi) => {
  const block = document.getElementById("profile-phone");
  if (!block) return;
  const token = PP._token?.();
  if (phoneFromApi) {
    block.innerHTML = `
      <p class="profile-phone-label">Телефон</p>
      <a href="tel:${phoneFromApi.replace(/\s/g, "")}" class="profile-phone-link">${phoneFromApi}</a>`;
    return;
  }
  if (!token) {
    block.innerHTML = `
      <p class="profile-phone-label">Контакт</p>
      <a href="${PP.loginUrl(location.pathname + location.search)}" class="btn btn-secondary btn-block">Увійти, щоб відкрити телефон</a>`;
    return;
  }
  let me = null;
  try {
    me = await PP.fetchMe();
  } catch {
    block.hidden = true;
    return;
  }
  if (me.role !== "parent") {
    block.innerHTML = `<p class="profile-phone-hint">Телефон доступний лише батькам з активною підпискою.</p>`;
    return;
  }

  let active = null;
  try {
    active = PP.findActiveSubscription(await PP.fetchSubscriptions());
  } catch {
    active = null;
  }

  const statusHtml = active
    ? `<div class="profile-phone-hint profile-phone-hint--ok" id="profile-unlock-hint">Підписка активна</div>`
    : `<div class="profile-phone-hint profile-phone-hint--error" id="profile-unlock-hint">${PP._profilePhoneSubscribeHint()}</div>`;

  block.innerHTML = `
    <p class="profile-phone-label">Телефон</p>
    <button type="button" class="btn btn-primary btn-block" id="profile-unlock-btn">📞 Показати телефон</button>
    ${statusHtml}`;
  PP._bindProfilePhoneUnlock(
    block,
    nannyId,
    document.getElementById("profile-unlock-btn"),
    document.getElementById("profile-unlock-hint")
  );
};
