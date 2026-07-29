/* Phone (+380), email and password live validation (UA messages, no native tooltips) */
window.PP = window.PP || {};

PP.UA_PHONE_RE = /^\+380\d{9}$/;
PP.EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;

PP.normalizeUaPhone = (raw) => {
  let digits = String(raw || "").replace(/\D/g, "");
  if (digits.startsWith("380")) digits = digits.slice(3);
  else if (digits.startsWith("0")) digits = digits.slice(1);
  return `+380${digits.slice(0, 9)}`;
};

PP.isValidUaPhone = (value) => PP.UA_PHONE_RE.test(String(value || "").trim());

PP.isValidEmail = (value) => PP.EMAIL_RE.test(String(value || "").trim());

PP.getPhoneError = (value) => {
  const v = String(value || "").trim();
  if (!v || v === "+380") return "Вкажіть номер телефону";
  if (!PP.isValidUaPhone(v)) return "Формат: +380XXXXXXXXX";
  return "";
};

PP.getEmailError = (value, { required = false } = {}) => {
  const v = String(value || "").trim();
  if (!v) return required ? "Вкажіть email" : "";
  if (!PP.isValidEmail(v)) return "Некоректний email";
  return "";
};

PP.getPasswordMinLength = (input) => {
  if (!input?.hasAttribute("minlength")) return 0;
  const n = Number(input.getAttribute("minlength"));
  return Number.isFinite(n) && n > 0 ? n : 0;
};

PP.getPasswordError = (value, { required = false, minLength = 0 } = {}) => {
  const v = String(value || "");
  if (!v) return required ? "Вкажіть пароль" : "";
  if (minLength && v.length < minLength) {
    return `Пароль має містити щонайменше ${minLength} символів`;
  }
  return "";
};

PP._ensureFieldErrorEl = (input) => {
  const id = input.id ? `${input.id}-error` : "";
  let el = id ? document.getElementById(id) : null;
  if (!el && input.nextElementSibling?.classList?.contains("field-error")) {
    el = input.nextElementSibling;
  }
  if (!el) {
    el = document.createElement("p");
    el.className = "field-error";
    el.setAttribute("role", "alert");
    if (id) el.id = id;
    input.insertAdjacentElement("afterend", el);
  }
  if (id && !input.getAttribute("aria-describedby")?.includes(id)) {
    const prev = input.getAttribute("aria-describedby") || "";
    input.setAttribute("aria-describedby", `${prev} ${id}`.trim());
  }
  return el;
};

PP.setFieldError = (input, message) => {
  if (!input) return;
  const el = PP._ensureFieldErrorEl(input);
  const invalid = Boolean(message);
  input.classList.toggle("is-invalid", invalid);
  input.setAttribute("aria-invalid", invalid ? "true" : "false");
  input.setCustomValidity?.(message || "");
  el.textContent = message || "";
  el.hidden = !invalid;
};

PP.clearFieldError = (input) => PP.setFieldError(input, "");

PP.validatePhoneField = (input, { normalize = true } = {}) => {
  if (!input) return false;
  if (normalize) {
    const next = PP.normalizeUaPhone(input.value);
    if (input.value !== next) input.value = next;
  }
  const error = PP.getPhoneError(input.value);
  PP.setFieldError(input, error);
  return !error;
};

PP.validateEmailField = (input) => {
  if (!input) return true;
  const required = input.hasAttribute("required");
  const error = PP.getEmailError(input.value, { required });
  PP.setFieldError(input, error);
  return !error;
};

PP.validatePasswordField = (input) => {
  if (!input) return true;
  const required = input.hasAttribute("required");
  const minLength = PP.getPasswordMinLength(input);
  let error = PP.getPasswordError(input.value, { required, minLength });
  if (!error && input.name === "password_confirm") {
    const pwd = input.form?.querySelector(
      'input[type="password"]:not([name="password_confirm"])'
    );
    if (pwd && input.value !== pwd.value) error = "Паролі не збігаються";
  }
  PP.setFieldError(input, error);
  return !error;
};

PP.validateRequiredField = (el) => {
  if (!el || !el.hasAttribute("required")) return true;
  if (
    el.matches(
      'input[type="email"], input[type="password"], input[type="tel"], input[name="phone"], input[type="hidden"], input[type="file"], input[type="checkbox"], input[type="radio"], input[type="submit"], input[type="button"]'
    )
  ) {
    return true;
  }
  const error = String(el.value || "").trim() ? "" : "Заповніть поле";
  PP.setFieldError(el, error);
  return !error;
};

PP.bindPhoneField = (input) => {
  if (!input || input.dataset.ppValidateBound) return;
  input.dataset.ppValidateBound = "1";
  input.setAttribute("required", "");
  input.setAttribute("maxlength", "13");
  input.setAttribute("autocomplete", input.getAttribute("autocomplete") || "tel");
  input.setAttribute("inputmode", "tel");

  if (!input.value || input.value === "+380") {
    input.value = "+380";
  } else {
    input.value = PP.normalizeUaPhone(input.value);
  }

  input.addEventListener("focus", () => {
    if (!input.value) input.value = "+380";
  });

  input.addEventListener("input", () => {
    const caretEnd = input.selectionStart === input.value.length;
    input.value = PP.normalizeUaPhone(input.value);
    if (caretEnd) {
      const len = input.value.length;
      try {
        input.setSelectionRange(len, len);
      } catch {
        /* iOS Safari may ignore for some input modes */
      }
    }
    PP.validatePhoneField(input, { normalize: false });
  });

  input.addEventListener("blur", () => {
    PP.validatePhoneField(input);
  });
};

PP.bindEmailField = (input) => {
  if (!input || input.dataset.ppValidateBound) return;
  input.dataset.ppValidateBound = "1";
  input.setAttribute("inputmode", input.getAttribute("inputmode") || "email");
  input.setAttribute("autocomplete", input.getAttribute("autocomplete") || "email");

  input.addEventListener("input", () => {
    PP.validateEmailField(input);
  });

  input.addEventListener("blur", () => {
    PP.validateEmailField(input);
  });
};

PP.bindPasswordField = (input) => {
  if (!input || input.dataset.ppValidateBound) return;
  input.dataset.ppValidateBound = "1";

  const syncConfirm = () => {
    const confirm = input.form?.querySelector('input[name="password_confirm"]');
    if (confirm && confirm !== input && confirm.value) PP.validatePasswordField(confirm);
  };

  input.addEventListener("input", () => {
    PP.validatePasswordField(input);
    if (input.name !== "password_confirm") syncConfirm();
  });

  input.addEventListener("blur", () => {
    PP.validatePasswordField(input);
  });
};

PP.disableNativeFormValidation = (root = document) => {
  root.querySelectorAll("form").forEach((form) => {
    if (
      form.querySelector(
        'input[type="email"], input[type="password"], input[type="tel"], input[name="phone"]'
      )
    ) {
      form.setAttribute("novalidate", "");
    }
  });
};

PP.initFieldValidation = (root = document) => {
  PP.disableNativeFormValidation(root);
  root.querySelectorAll('input[type="tel"], input[name="phone"]').forEach(PP.bindPhoneField);
  root.querySelectorAll('input[type="email"]').forEach(PP.bindEmailField);
  root.querySelectorAll('input[type="password"]').forEach(PP.bindPasswordField);
};

PP.validateFormContacts = (form) => {
  if (!form) return true;
  form.setAttribute("novalidate", "");
  let ok = true;
  form.querySelectorAll('input[type="tel"], input[name="phone"]').forEach((input) => {
    if (!PP.validatePhoneField(input)) ok = false;
  });
  form.querySelectorAll('input[type="email"]').forEach((input) => {
    if (!PP.validateEmailField(input)) ok = false;
  });
  form.querySelectorAll('input[type="password"]').forEach((input) => {
    if (!PP.validatePasswordField(input)) ok = false;
  });
  form.querySelectorAll("input[required], textarea[required]").forEach((el) => {
    if (!PP.validateRequiredField(el)) ok = false;
  });
  if (!ok) {
    const first = form.querySelector(".field.is-invalid, input.is-invalid, textarea.is-invalid");
    first?.focus?.({ preventScroll: false });
  }
  return ok;
};

document.addEventListener(
  "submit",
  (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (
      !form.querySelector(
        'input[type="tel"], input[name="phone"], input[type="email"], input[type="password"]'
      )
    ) {
      return;
    }
    form.setAttribute("novalidate", "");
    if (!PP.validateFormContacts(form)) {
      e.preventDefault();
      e.stopPropagation();
    }
  },
  true
);

const bootFieldValidation = () => PP.initFieldValidation();
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootFieldValidation);
} else {
  bootFieldValidation();
}
