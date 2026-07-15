/* Custom Select — brand-styled dropdown replaces select.field */
window.PP = window.PP || {};

PP.CustomSelect = (() => {
  const CHEVRON = `<svg class="cs-chevron" viewBox="0 0 16 16" fill="none" width="16" height="16" aria-hidden="true"><path stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" d="M4 6l4 4 4-4"/></svg>`;

  function build(sel) {
    sel.setAttribute('data-cs-init', '1');

    const root    = document.createElement('div');
    root.className = 'cs-root';

    const trigger = document.createElement('button');
    trigger.type  = 'button';
    trigger.className = 'cs-trigger';
    trigger.setAttribute('aria-haspopup', 'listbox');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.innerHTML = `<span class="cs-value"></span>${CHEVRON}`;

    const valueEl = trigger.querySelector('.cs-value');

    if (sel.id) {
      trigger.id = `${sel.id}-cs`;
      const lbl = document.querySelector(`label[for="${sel.id}"]`);
      if (lbl) lbl.setAttribute('for', trigger.id);
    }

    const menu = document.createElement('ul');
    menu.className = 'cs-menu';
    menu.setAttribute('role', 'listbox');
    menu.hidden = true;

    sel.parentNode.insertBefore(root, sel);
    root.appendChild(trigger);
    root.appendChild(menu);
    root.appendChild(sel);

    sel.setAttribute('aria-hidden', 'true');
    sel.tabIndex = -1;
    sel.style.cssText = 'position:absolute;opacity:0;pointer-events:none;width:0;height:0;overflow:hidden;';

    populate(sel, menu, valueEl, root, trigger);

    new MutationObserver(() => populate(sel, menu, valueEl, root, trigger))
      .observe(sel, { childList: true, subtree: true });

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      menu.hidden ? openMenu(root, trigger, menu) : closeMenu(root, trigger, menu);
    });

    trigger.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { closeMenu(root, trigger, menu); return; }
      if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        if (menu.hidden) openMenu(root, trigger, menu);
        (menu.querySelector('.cs-option.is-selected:not(.is-disabled)') || menu.querySelector('.cs-option:not(.is-disabled)'))?.focus();
      }
    });

    menu.addEventListener('keydown', (e) => {
      const opts = [...menu.querySelectorAll('.cs-option:not(.is-disabled)')];
      const idx  = opts.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); opts[Math.min(idx + 1, opts.length - 1)]?.focus(); return; }
      if (e.key === 'ArrowUp')   { e.preventDefault(); idx <= 0 ? trigger.focus() : opts[idx - 1]?.focus(); return; }
      if (e.key === 'Escape')    { closeMenu(root, trigger, menu); trigger.focus(); return; }
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); document.activeElement?.click(); }
    });
  }

  function populate(sel, menu, valueEl, root, trigger) {
    menu.innerHTML = '';
    const cur = sel.value;

    const appendOption = (opt) => {
      const disabled = opt.disabled;
      const li = document.createElement('li');
      li.className = 'cs-option' + (opt.value === cur && !disabled ? ' is-selected' : '') + (disabled ? ' is-disabled' : '');
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', String(opt.value === cur && !disabled));
      if (disabled) li.setAttribute('aria-disabled', 'true');
      li.setAttribute('data-value', opt.value);
      li.tabIndex = -1;
      li.textContent = opt.text;
      if (!disabled) {
        li.addEventListener('click', () => pick(li, sel, menu, valueEl, opt.value, root, trigger));
      }
      menu.appendChild(li);
    };

    [...sel.children].forEach((child) => {
      if (child.tagName === 'OPTGROUP') {
        const head = document.createElement('li');
        head.className = 'cs-group-label';
        head.setAttribute('role', 'presentation');
        head.textContent = child.label;
        menu.appendChild(head);
        [...child.querySelectorAll('option')].forEach(appendOption);
        return;
      }
      if (child.tagName === 'OPTION') appendOption(child);
    });

    const cur_opt = [...sel.options].find(o => o.value === cur && !o.disabled) || sel.options[0];
    if (cur_opt) valueEl.textContent = cur_opt.text;
  }

  function pick(li, sel, menu, valueEl, value, root, trigger) {
    sel.value = value;
    sel.dispatchEvent(new Event('input', { bubbles: true }));
    sel.dispatchEvent(new Event('change', { bubbles: true }));
    menu.querySelectorAll('.cs-option').forEach(o => {
      const s = o.dataset.value === value;
      o.classList.toggle('is-selected', s);
      o.setAttribute('aria-selected', String(s));
    });
    const opt = [...sel.options].find(o => o.value === value);
    if (opt) valueEl.textContent = opt.text;
    closeMenu(root, trigger, menu);
    trigger?.focus();
  }

  /* ── Portal: переміщаємо меню в body щоб уникнути overflow:hidden ── */

  function placeMenu(trigger, menu) {
    const rect = trigger.getBoundingClientRect();
    const vw   = window.innerWidth;
    const vh   = window.innerHeight;
    const spaceBelow = vh - rect.bottom;
    const spaceAbove = rect.top;

    const left = Math.min(rect.left, vw - rect.width - 8);

    menu.style.cssText = [
      'position:fixed',
      `width:${rect.width}px`,
      `left:${left}px`,
      'right:auto',
      'z-index:9999',
    ].join(';') + ';';

    if (spaceBelow >= 120 || spaceBelow >= spaceAbove) {
      menu.style.top       = (rect.bottom + 4) + 'px';
      menu.style.bottom    = 'auto';
      menu.style.maxHeight = Math.max(spaceBelow - 16, 80) + 'px';
    } else {
      menu.style.bottom    = (vh - rect.top + 4) + 'px';
      menu.style.top       = 'auto';
      menu.style.maxHeight = Math.max(spaceAbove - 16, 80) + 'px';
    }
  }

  function openMenu(root, trigger, menu) {
    document.querySelectorAll('.cs-root.is-open').forEach(r => {
      const t = r.querySelector('.cs-trigger');
      const m = r._csMenu;
      if (m) closeMenu(r, t, m);
    });

    root._csMenu = menu;
    document.body.appendChild(menu);
    menu.hidden = false;
    root.classList.add('is-open');
    trigger.setAttribute('aria-expanded', 'true');

    placeMenu(trigger, menu);

    (menu.querySelector('.cs-option.is-selected:not(.is-disabled)') || menu.querySelector('.cs-option:not(.is-disabled)'))?.focus();
  }

  function closeMenu(root, trigger, menu) {
    if (!root || !menu) return;
    if (menu.parentNode === document.body) {
      root.appendChild(menu);
    }
    menu.style.cssText = '';
    menu.hidden = true;
    root.classList.remove('is-open');
    trigger?.setAttribute('aria-expanded', 'false');
  }

  document.addEventListener('click', (e) => {
    document.querySelectorAll('.cs-root.is-open').forEach(r => {
      const t = r.querySelector('.cs-trigger');
      const m = r._csMenu;
      if (m && !m.contains(e.target) && !t?.contains(e.target)) {
        closeMenu(r, t, m);
      }
    });
  });

  function repositionOpenMenus() {
    document.querySelectorAll('.cs-root.is-open').forEach(r => {
      const t = r.querySelector('.cs-trigger');
      const m = r._csMenu;
      if (m && !m.hidden) placeMenu(t, m);
    });
  }

  window.addEventListener('resize', repositionOpenMenus, { passive: true });
  window.addEventListener('scroll', repositionOpenMenus, { passive: true, capture: true });

  function refresh(sel) {
    if (!sel?.dataset?.csInit) return;
    const root = sel.closest('.cs-root');
    if (!root) return;
    const menu = root._csMenu || root.querySelector('.cs-menu');
    const trigger = root.querySelector('.cs-trigger');
    const valueEl = trigger?.querySelector('.cs-value');
    if (menu && trigger && valueEl) populate(sel, menu, valueEl, root, trigger);
  }

  function init(container) {
    (container || document).querySelectorAll('select.field:not([data-cs-init])').forEach(build);
  }

  if (typeof PP.renderFilters === 'function') {
    const _orig = PP.renderFilters;
    PP.renderFilters = function(container, ...args) {
      _orig.call(this, container, ...args);
      if (container) init(container);
    };
  }

  document.addEventListener('DOMContentLoaded', () => init());

  return { init, refresh };
})();
