/* Auth: login, register, forgot password, OAuth */
window.PP = window.PP || {};

PP.authRedirectAfterLogin = (role) => {
  const params = new URLSearchParams(location.search);
  const next = params.get("next");
  if (next && next.startsWith("/") && !next.startsWith("//")) {
    location.replace(next);
    return;
  }
  location.replace(PP.authHomeForRole(role));
};

PP.redirectIfAuthenticated = async () => {
  const path = PP.normalizePath(location.pathname);
  if (!PP.isAuthPage(path)) return;

  const params = new URLSearchParams(location.search);
  const next = params.get("next") || "";

  if (params.get("reauth") === "1" && PP.needsParentAccount(next)) {
    const ok = await PP.waitForSession();
    if (!ok) return;
    let role = PP.getSessionRole();
    if (!role) {
      await PP.syncSessionUser();
      role = PP.getSessionRole();
    }
    if (role === "parent") {
      PP.authRedirectAfterLogin(role);
    }
    return;
  }

  if (params.get("reauth") === "1" && PP.needsAdminAccount(next)) {
    const ok = await PP.waitForSession();
    if (!ok) return;
    let role = PP.getSessionRole();
    if (!role) {
      await PP.syncSessionUser();
      role = PP.getSessionRole();
    }
    if (PP.isPlatformAdmin()) {
      PP.authRedirectAfterLogin(role);
    }
    return;
  }

  if (params.get("reauth") === "1") return;

  if (PP.needsParentAccount(next)) {
    const role = PP.getSessionRole();
    if (role && role !== "parent") return;
  }

  if (PP.needsAdminAccount(next)) {
    if (!PP.isPlatformAdmin()) {
      const role = PP.getSessionRole();
      if (role && role !== "admin") return;
    }
  }

  const ok = await PP.waitForSession();
  if (!ok) return;
  const role = PP.getSessionRole() || "parent";
  PP.authRedirectAfterLogin(role);
};

PP.showReauthHint = () => {
  const card = document.querySelector(".auth-card");
  if (!card || document.getElementById("auth-reauth-hint")) return;
  const hint = document.createElement("p");
  hint.id = "auth-reauth-hint";
  hint.className = "auth-subtitle";
  hint.textContent = "Щоб написати няні, увійдіть під акаунтом батьків.";
  card.querySelector(".auth-subtitle")?.insertAdjacentElement("afterend", hint);
};

PP.showAdminReauthHint = () => {
  const card = document.querySelector(".auth-card");
  if (!card || document.getElementById("auth-reauth-hint")) return;
  const hint = document.createElement("p");
  hint.id = "auth-reauth-hint";
  hint.className = "auth-subtitle";
  hint.textContent = "Увійдіть під обліковим записом адміністратора.";
  card.querySelector(".auth-subtitle")?.insertAdjacentElement("afterend", hint);
};

PP.handleReauthPage = async () => {
  const params = new URLSearchParams(location.search);
  if (params.get("reauth") !== "1") return;

  const next = params.get("next") || "";
  if (PP.needsParentAccount(next)) PP.showReauthHint();
  if (PP.needsAdminAccount(next)) PP.showAdminReauthHint();

  const needsRoleSwitch = PP.needsParentAccount(next) || PP.needsAdminAccount(next);
  if (!needsRoleSwitch || !PP.hasStoredSession()) return;

  const ok = await PP.waitForSession();
  if (!ok) return;

  let role = PP.getSessionRole();
  if (!role) {
    await PP.syncSessionUser();
    role = PP.getSessionRole();
  }

  if (PP.needsParentAccount(next) && role && role !== "parent") {
    PP._refreshPromise = null;
    PP.clearSession();
  }
  if (PP.needsAdminAccount(next) && !PP.isPlatformAdmin({ role })) {
    PP._refreshPromise = null;
    PP.clearSession();
  }
};

PP.initAuth = async () => {
  await PP.handleReauthPage();
  await PP.redirectIfAuthenticated();
  PP.initRegisterRoleFromUrl?.();

  document.querySelectorAll(".auth-role-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".auth-role-option").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const roleInput = document.getElementById("role-input");
      if (roleInput) roleInput.value = btn.dataset.role;
      PP.toggleRegisterDocs?.(btn.dataset.role);
    });
  });

  PP.initOAuthButtons?.();
  PP.initRegisterDocInputs?.();
  PP.initRegisterForm?.();
  PP.initLoginForm?.();
  PP.initForgotPassword?.();
  PP.initResetPassword?.();
};

PP.toggleRegisterDocs = (role) => {
  const panel = document.getElementById("register-docs-panel");
  if (panel) panel.hidden = role !== "nanny";
};

PP.formatRegisterFileSize = (bytes) => {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
};

PP.initRegisterDocInputs = () => {
  const panel = document.getElementById("register-docs-panel");
  if (!panel) return;

  panel.querySelectorAll(".doc-file-input").forEach((wrap) => {
    const input = wrap.querySelector('input[type="file"]');
    const labelTextEl = wrap.querySelector(".doc-file-label-text");
    const selectedEl = wrap.querySelector(".doc-file-selected");
    const nameEl = wrap.querySelector(".doc-file-selected-name");
    if (!input) return;

    const resetUi = () => {
      wrap.classList.remove("has-file");
      if (labelTextEl) labelTextEl.textContent = "Обрати файл (PDF, JPG, PNG)";
      if (nameEl) nameEl.textContent = "";
      selectedEl?.setAttribute("hidden", "");
    };

    const showFile = (file) => {
      wrap.classList.add("has-file");
      if (labelTextEl) labelTextEl.textContent = "Змінити файл";
      if (nameEl) {
        nameEl.textContent = `${file.name} · ${PP.formatRegisterFileSize(file.size)}`;
      }
      selectedEl?.removeAttribute("hidden");
    };

    input.addEventListener("change", () => {
      const file = input.files?.[0];
      if (file) showFile(file);
      else resetUi();
    });
  });
};

PP.initRegisterRoleFromUrl = () => {
  const params = new URLSearchParams(location.search);
  const role = params.get("role");
  if (role !== "nanny" && role !== "parent") return;
  const btn = document.querySelector(`.auth-role-option[data-role="${role}"]`);
  if (!btn) return;
  document.querySelectorAll(".auth-role-option").forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  const roleInput = document.getElementById("role-input");
  if (roleInput) roleInput.value = role;
  PP.toggleRegisterDocs?.(role);
};

PP.getAuthRole = () => document.getElementById("role-input")?.value || "parent";

PP.completeOAuthLogin = async (provider, payload) => {
  const role = PP.getAuthRole();
  const data = await PP.authOAuth(provider, payload, role);
  const params = new URLSearchParams(location.search);
  const next = params.get("next") || "";
  const isReauth = params.get("reauth") === "1";

  if (isReauth && PP.needsParentAccount(next) && data.user?.role !== "parent") {
    PP.showToast(
      "Чат з нянями доступний лише для акаунта батьків. Зареєструйтеся як батьки або увійдіть під іншим email.",
      "error"
    );
    return;
  }

  if (isReauth && PP.needsAdminAccount(next) && !PP.isPlatformAdmin(data.user)) {
    PP.showToast("Доступ лише для адміністраторів. Увійдіть під іншим обліковим записом.", "error");
    PP.clearSession();
    return;
  }

  PP.saveSession(data);
  PP.authRedirectAfterLogin(data.user.role);
};

PP.initOAuthButtons = async () => {
  const btns = document.querySelectorAll(".auth-oauth-btn");
  if (!btns.length) return;

  let status = { google: false, facebook: false, apple: false, google_client_id: "", facebook_app_id: "", apple_client_id: "" };
  try {
    status = await PP.authOAuthStatus();
  } catch {
    /* offline */
  }

  btns.forEach((btn) => {
    const provider = btn.dataset.provider;
    if (provider && !status[provider]) {
      btn.disabled = true;
      btn.title = "Налаштуйте OAuth у backend/.env";
      return;
    }
    btn.disabled = false;
    btn.title = "";
  });

  if (status.google && status.google_client_id) {
    PP.initGoogleOAuth(status.google_client_id);
  }

  if (status.facebook && status.facebook_app_id) {
    PP.initFacebookOAuth(status.facebook_app_id, btns);
  }

  if (status.apple && status.apple_client_id) {
    PP.initAppleOAuth(status.apple_client_id, btns);
  }

  btns.forEach((btn) => {
    const provider = btn.dataset.provider;
    if (btn.disabled || provider === "google" || provider === "facebook" || provider === "apple") return;
    btn.addEventListener("click", () => {
      PP.showToast("OAuth провайдер не підключено.", "error");
    });
  });
};

PP.initGoogleOAuth = (clientId) => {
  const btn = document.querySelector('.auth-oauth-btn[data-provider="google"]');
  if (!btn || btn.dataset.oauthReady) return;
  btn.dataset.oauthReady = "1";

  const loadScript = () =>
    new Promise((resolve, reject) => {
      if (window.google?.accounts?.id) {
        resolve();
        return;
      }
      const s = document.createElement("script");
      s.src = "https://accounts.google.com/gsi/client";
      s.async = true;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    try {
      await loadScript();
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response) => {
          try {
            await PP.completeOAuthLogin("google", { id_token: response.credential });
          } catch (err) {
            PP.showToast(err.message || "Помилка OAuth", "error");
            btn.disabled = false;
          }
        },
      });
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          window.google.accounts.oauth2
            .initTokenClient({
              client_id: clientId,
              scope: "email profile openid",
              callback: async (tokenResponse) => {
                try {
                  await PP.completeOAuthLogin("google", { access_token: tokenResponse.access_token });
                } catch (err) {
                  PP.showToast(err.message || "Помилка OAuth", "error");
                  btn.disabled = false;
                }
              },
            })
            .requestAccessToken();
        }
      });
    } catch {
      PP.showToast("Не вдалося завантажити Google OAuth.", "error");
      btn.disabled = false;
    }
  });
};

PP.ensureFacebookSdk = (appId) => {
  if (PP._fbSdkPromise) return PP._fbSdkPromise;

  PP._fbSdkPromise = new Promise((resolve, reject) => {
    let settled = false;
    const done = (fn, value) => {
      if (settled) return;
      settled = true;
      fn(value);
    };

    const initSdk = () => {
      try {
        if (!PP._fbInited) {
          window.FB.init({
            appId: String(appId),
            cookie: true,
            xfbml: false,
            version: "v19.0",
          });
          PP._fbInited = true;
        }
        done(resolve, window.FB);
      } catch (err) {
        if (window.FB?.login) done(resolve, window.FB);
        else done(reject, err);
      }
    };

    if (window.FB?.init) {
      initSdk();
      return;
    }

    const prevInit = window.fbAsyncInit;
    window.fbAsyncInit = () => {
      try {
        if (typeof prevInit === "function") prevInit();
      } catch {
        /* ignore previous init errors */
      }
      initSdk();
    };

    const existing = document.querySelector('script[data-pp-fb-sdk="1"]');
    if (!existing) {
      const s = document.createElement("script");
      s.src = "https://connect.facebook.net/uk_UA/sdk.js";
      s.async = true;
      s.dataset.ppFbSdk = "1";
      s.onerror = () => done(reject, new Error("Не вдалося завантажити Facebook SDK"));
      document.head.appendChild(s);
    }

    window.setTimeout(() => {
      if (!window.FB?.login) {
        done(reject, new Error("Таймаут завантаження Facebook SDK"));
      }
    }, 15000);
  });

  return PP._fbSdkPromise;
};

PP.initFacebookOAuth = (appId, btns) => {
  const btn = [...btns].find((b) => b.dataset.provider === "facebook");
  if (!btn || btn.dataset.oauthReady) return;
  btn.dataset.oauthReady = "1";

  // Preload SDK before click so FB.login runs inside a real user gesture.
  PP.ensureFacebookSdk(appId).catch((err) => {
    console.error("Facebook SDK preload failed", err);
  });

  btn.addEventListener("click", () => {
    if (!window.FB?.login) {
      PP.showToast("Facebook ще завантажується. Спробуйте ще раз через секунду.", "error");
      PP.ensureFacebookSdk(appId).catch((err) => {
        console.error("Facebook SDK load failed", err);
        PP.showToast(err.message || "Не вдалося завантажити Facebook SDK.", "error");
      });
      return;
    }

    btn.disabled = true;
    try {
      window.FB.login(
        async (response) => {
          if (!response?.authResponse?.accessToken) {
            btn.disabled = false;
            if (response?.status === "unknown") {
              PP.showToast("Вхід через Facebook скасовано або заблоковано браузером.", "error");
            }
            return;
          }
          try {
            await PP.completeOAuthLogin("facebook", { access_token: response.authResponse.accessToken });
          } catch (err) {
            console.error("Facebook OAuth backend error", err);
            PP.showToast(err.message || "Помилка OAuth", "error");
            btn.disabled = false;
          }
        },
        { scope: "email,public_profile", return_scopes: true }
      );
    } catch (err) {
      console.error("Facebook login error", err);
      PP.showToast(err.message || "Помилка входу через Facebook", "error");
      btn.disabled = false;
    }
  });
};

PP.initAppleOAuth = (clientId, btns) => {
  const btn = [...btns].find((b) => b.dataset.provider === "apple");
  if (!btn || btn.dataset.oauthReady) return;
  btn.dataset.oauthReady = "1";

  const loadScript = () =>
    new Promise((resolve, reject) => {
      if (window.AppleID) {
        resolve();
        return;
      }
      const s = document.createElement("script");
      s.src = "https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js";
      s.async = true;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    try {
      await loadScript();
      const redirectURI = `${window.location.origin}/login`;
      window.AppleID.auth.init({
        clientId,
        scope: "name email",
        redirectURI,
        usePopup: true,
      });
      const response = await window.AppleID.auth.signIn();
      const idToken = response?.authorization?.id_token;
      if (!idToken) throw new Error("Не отримано Apple token");
      await PP.completeOAuthLogin("apple", { id_token: idToken });
    } catch (err) {
      if (err?.error !== "popup_closed_by_user") {
        PP.showToast(err.message || "Помилка Apple Sign In", "error");
      }
      btn.disabled = false;
    }
  });
};

PP.initRegisterForm = () => {
  const form = document.getElementById("register-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (PP.validateFormContacts && !PP.validateFormContacts(form)) return;
    const role = PP.getAuthRole();
    const firstName = form.querySelector('[name="first_name"]')?.value?.trim() || "";
    const email = form.querySelector('[type="email"]')?.value?.trim();
    const password = form.querySelector('[type="password"]')?.value;
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    try {
      if (role === "nanny") {
        for (const type of PP.REQUIRED_NANNY_DOCS) {
          const input = document.querySelector(`[data-doc-type="${type}"]`);
          if (!input?.files?.[0]) {
            PP.showToast(`Завантажте ${PP.DOC_TYPES[type]} для реєстрації помічника.`, "error");
            btn.disabled = false;
            return;
          }
        }
      }
      const data = await PP.authRegister({
        email,
        password,
        role,
        first_name: firstName,
      });
      PP.saveSession(data);
      if (role === "nanny") {
        PP.showRegisterStep2?.(form);
        await PP.uploadRegisterDocs?.();
        location.href = `${PP.ROUTES.nannyDocuments}?onboarding=1`;
        return;
      }
      PP.authRedirectAfterLogin(data.user.role);
    } catch (err) {
      PP.showToast(err.message || "Помилка реєстрації", "error");
    } finally {
      btn.disabled = false;
    }
  });
};

PP.showRegisterStep2 = (form) => {
  form.hidden = true;
  const step2 = document.getElementById("register-step2");
  if (step2) step2.hidden = false;
};

PP.uploadRegisterDocs = async () => {
  const inputs = document.querySelectorAll("[data-doc-type]");
  for (const input of inputs) {
    const file = input.files?.[0];
    if (!file) continue;
    await PP.uploadDocument(input.dataset.docType, file);
  }
};

PP.setLoginFormError = (form, message = "") => {
  const errEl = document.getElementById("login-error");
  const emailInput = form?.querySelector('[type="email"]');
  const passwordInput = form?.querySelector('[type="password"]');
  const msg = String(message || "").trim();

  if (errEl) {
    errEl.textContent = msg;
    errEl.hidden = !msg;
  }

  [emailInput, passwordInput].forEach((input) => {
    if (!input) return;
    input.classList.toggle("is-invalid", Boolean(msg));
    input.setAttribute("aria-invalid", msg ? "true" : "false");
  });
};

PP.initLoginForm = () => {
  const form = document.getElementById("login-form");
  if (!form) return;

  form.addEventListener("input", () => {
    if (document.getElementById("login-error")?.hidden === false) {
      PP.setLoginFormError(form, "");
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    PP.setLoginFormError(form, "");
    if (PP.validateFormContacts && !PP.validateFormContacts(form)) return;
    const email = form.querySelector('[type="email"]')?.value?.trim();
    const password = form.querySelector('[type="password"]')?.value;
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    try {
      const params = new URLSearchParams(location.search);
      const data = await PP.authLogin(email, password);
      PP.saveSession(data);

      const next = params.get("next") || "";
      const isReauth = params.get("reauth") === "1";
      if (isReauth && PP.needsParentAccount(next) && data.user?.role !== "parent") {
        const msg =
          "Чат з нянями доступний лише для акаунта батьків. Зареєструйтеся як батьки або увійдіть під іншим email.";
        PP.setLoginFormError(form, msg);
        PP.showToast(msg, "error");
        PP.clearSession();
        return;
      }

      if (isReauth && PP.needsAdminAccount(next) && !PP.isPlatformAdmin(data.user)) {
        const msg = "Доступ лише для адміністраторів. Увійдіть під іншим обліковим записом.";
        PP.setLoginFormError(form, msg);
        PP.showToast(msg, "error");
        PP.clearSession();
        return;
      }

      PP.authRedirectAfterLogin(data.user.role);
    } catch (err) {
      const msg = err?.message || "Невірний email або пароль.";
      PP.setLoginFormError(form, msg);
      PP.showToast(msg, "error");
      form.querySelector('[type="password"]')?.focus?.();
    } finally {
      btn.disabled = false;
    }
  });
};

PP.initForgotPassword = () => {
  const form = document.getElementById("forgot-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (PP.validateFormContacts && !PP.validateFormContacts(form)) return;
    const email = form.querySelector('[type="email"]')?.value?.trim();
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    try {
      await PP.authPasswordReset(email);
      PP.showToastThenGo("Якщо email існує, лист надіслано.", "success", PP.ROUTES.login);
    } catch (err) {
      PP.showToast(err.message || "Не вдалося надіслати лист.", "error");
    } finally {
      btn.disabled = false;
    }
  });
};

PP.initResetPassword = () => {
  const form = document.getElementById("reset-form");
  if (!form) return;

  const params = new URLSearchParams(location.search);
  const uid = params.get("uid");
  const token = params.get("token");
  const errEl = document.getElementById("reset-error");

  if (!uid || !token) {
    if (errEl) {
      errEl.hidden = false;
      errEl.textContent = "Невалідне посилання для скидання пароля.";
    }
    form.hidden = true;
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (PP.validateFormContacts && !PP.validateFormContacts(form)) return;
    const password = form.querySelector('[type="password"]')?.value;
    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    try {
      await PP.authPasswordResetConfirm(uid, token, password);
      PP.showToastThenGo("Пароль оновлено. Увійдіть з новим паролем.", "success", PP.ROUTES.login);
    } catch (err) {
      PP.showToast(err.message || "Не вдалося оновити пароль.", "error");
    } finally {
      btn.disabled = false;
    }
  });
};
