#!/usr/bin/env python3
"""Cabinet + Admin HTML pages"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from generate_public import CSS_ADMIN, CSS_CABINET, page

CAB = CSS_CABINET
INIT = "PP.initCabinetPage();"

# Parent cabinet
page("cabinet/parent/index.html", "Кабінет Батьків", "Дашборд", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="parent-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="parent-nav"></nav></aside>
  <div><h1 class="cabinet-title">Дашборд</h1><p class="cabinet-subtitle">Ласкаво прosimo!</p>
  <div class="stat-grid"><div class="card stat-card"><div class="stat-value">0</div><div class="stat-label">Обрані</div></div>
  <div class="card stat-card"><div class="stat-value">0</div><div class="stat-label">Чати</div></div>
  <div class="card stat-card"><div class="stat-value">0</div><div class="stat-label">Контакти</div></div>
  <div class="card stat-card"><div class="stat-value">—</div><div class="stat-label">Підписка</div></div></div>
  <h2 class="section-heading-sm">Рекомендовані</h2><div class="catalog-grid" id="dash-nannies"></div></div>
</div>
""", css=CAB, init=INIT)

page("cabinet/parent/search.html", "Пошук — Кабінет", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="parent-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="parent-nav"></nav></aside>
  <div><h1 class="cabinet-title">Пошук нянь</h1>
  <button class="btn btn-secondary filters-mobile-toggle btn-block" id="filters-toggle">Фільтри</button>
  <div class="catalog-layout"><aside class="filters-desktop"><div class="card filters-panel"><div class="filters-panel-body" id="filters-desktop"></div></div></aside>
  <div><p id="results-count"></p><div class="catalog-grid" id="catalog-grid"></div></div></div></div>
</div>
""", css=CAB, init=INIT + " PP.initCatalog();")

page("cabinet/parent/profile.html", "Профіль Батьків", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="parent-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="parent-nav"></nav></aside>
  <div class="cabinet-main parent-profile-page">
    <div class="cabinet-page-head">
      <h1 class="cabinet-title">Профіль</h1>
      <p class="cabinet-subtitle">Заповніть дані та додайте фото — няні побачать профіль після відкриття контакту</p>
    </div>
    <div class="profile-page-grid">
      <form class="card profile-form" id="parent-profile-form">
        <div class="profile-photo-section">
          <div class="profile-avatar-wrap" id="profile-avatar-wrap">
            <img class="profile-avatar-img" id="profile-photo-preview" alt="" width="112" height="112" hidden>
            <span class="profile-avatar-fallback" id="profile-photo-fallback" aria-hidden="true">👤</span>
          </div>
          <div class="profile-photo-actions">
            <span class="label">Фото профілю</span>
            <p class="profile-photo-hint">JPEG, PNG або WebP, до 5 МБ. Квадратне фото виглядає найкраще.</p>
            <input type="file" class="profile-photo-input" id="profile-photo-input" accept="image/jpeg,image/png,image/webp" hidden>
            <button type="button" class="btn btn-secondary profile-photo-btn" id="profile-photo-btn">Змінити фото</button>
          </div>
        </div>
        <div class="form-row form-row-2">
          <div><label class="label" for="pf-first-name">Ім'я</label><input class="field" id="pf-first-name" name="first_name" autocomplete="given-name"></div>
          <div><label class="label" for="pf-last-name">Прізвище</label><input class="field" id="pf-last-name" name="last_name" autocomplete="family-name"></div>
        </div>
        <div class="form-row form-row-2">
          <div><label class="label" for="pf-birth-date">Дата народження</label><input class="field" id="pf-birth-date" name="birth_date" type="date"></div>
          <div><label class="label" for="pf-phone">Телефон</label><input class="field" id="pf-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+380"></div>
        </div>
        <div class="form-row">
          <label class="label" for="pf-city">Місто</label>
          <input class="field" id="pf-city" name="city" readonly>
        </div>
        <fieldset class="profile-fieldset">
          <legend>Про дітей</legend>
          <div class="form-row form-row-2">
            <div><label class="label" for="pf-children-count">Кількість дітей</label><input type="number" class="field" id="pf-children-count" name="children_count" min="0" inputmode="numeric"></div>
            <div><label class="label" for="pf-children-ages">Вік дітей</label><input class="field" id="pf-children-ages" name="children_ages" placeholder="3, 6"></div>
          </div>
          <div class="form-row">
            <label class="label" for="pf-special-needs">Особливі потреби</label>
            <textarea class="field" id="pf-special-needs" rows="4" name="special_needs" placeholder="Алергії, особливості розвитку, побажання до догляду"></textarea>
          </div>
        </fieldset>
        <div class="profile-form-actions">
          <button type="submit" class="btn btn-primary">Зберегти зміни</button>
        </div>
      </form>
      <aside class="card profile-preview-card" aria-label="Превʼю профілю">
        <h2 class="profile-preview-title">Як бачать няні</h2>
        <div id="profile-card-preview" class="profile-preview-inner"></div>
        <ul class="profile-tips-list">
          <li>Якісне фото допомагає няням краще вас розпізнати</li>
          <li>Детальна інформація про дітей полегшує підбір</li>
          <li>Контактні дані доступні після відкриття чату</li>
        </ul>
      </aside>
    </div>
  </div>
</div>
""", css=CAB, init=INIT)

page("cabinet/parent/favorites.html", "Обране", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="parent-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="parent-nav"></nav></aside>
  <div class="cabinet-main parent-favorites-page">
    <div class="cabinet-page-head">
      <h1 class="cabinet-title">Обране</h1>
      <p class="cabinet-subtitle">Збережені профілі нянь — порівняйте та напишіть обраним</p>
    </div>
    <div class="favorites-toolbar card" id="favorites-toolbar" hidden>
      <p class="favorites-count" id="favorites-count" aria-live="polite"></p>
      <a href="/cabinet/parent/search" class="btn btn-secondary favorites-search-btn">Знайти ще нянь</a>
    </div>
    <div class="favorites-grid" id="fav-grid" aria-live="polite" aria-busy="true"></div>
  </div>
</div>
""", css=CAB, init=INIT)

CHAT_FORM = (
    '<input type="file" hidden accept="image/*,.pdf,.doc,.docx">'
    '<button type="button" class="chat-attach" aria-label="Вкладення">📎</button>'
    '<input class="field" type="text" placeholder="Повідомлення" enterkeyhint="send" autocomplete="off">'
    '<button type="submit" class="btn btn-primary" aria-label="Надіслати">→</button>'
)
CHAT_INIT = INIT
CHAT_JS = '  <script src="/js/chat.js"></script>\n'

page("cabinet/parent/chat.html", "Чат", "", f"""
<div class="container cabinet-chat-wrap">
  <h1 class="cabinet-title">Чат</h1>
  <div class="card chat-layout"><div class="chat-list"></div>
  <div class="chat-window"><div class="chat-header">Повідомлення</div>
  <div class="chat-messages" id="chat-messages"></div>
  <form class="chat-input-bar" id="chat-form">{CHAT_FORM}</form>
  </div></div></div>
""", css=CAB, init=CHAT_INIT, extra_js=CHAT_JS)

page("cabinet/parent/payments.html", "Платежі", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="parent-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="parent-nav"></nav></aside>
  <div><h1 class="cabinet-title">Платежі</h1><p class="cabinet-subtitle">LiqPay · WayForPay · Fondy</p>
  <div id="pay-pending" class="pay-pending-banner" hidden></div>
  <div id="pay-subscription" class="pay-subscription card" hidden></div>
  <div id="pay-provider-picker"></div>
  <div class="pricing-grid" id="pay-grid"></div></div>
</div>
""", css=CAB, init=INIT)

page("cabinet/parent/reviews.html", "Відгуки", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="parent-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="parent-nav"></nav></aside>
  <div class="cabinet-main parent-reviews-page">
    <div class="cabinet-page-head">
      <h1 class="cabinet-title">Залишити відгук</h1>
      <p class="cabinet-subtitle">Поділіться враженнями після співпраці з нянею</p>
    </div>
    <div class="review-success card" id="review-success" hidden aria-live="polite">
      <div class="review-success-icon" aria-hidden="true">✓</div>
      <h2 class="review-success-title">Дякуємо за відгук!</h2>
      <p class="review-success-text" id="review-success-text"></p>
      <div class="review-success-stars" id="review-success-stars" aria-hidden="true"></div>
      <p class="review-success-note">Ваш відгук опубліковано в профілі няні та допоможе іншим батькам обрати надійну поміч.</p>
      <div class="review-success-actions">
        <button type="button" class="btn btn-primary" id="review-success-again">Залишити ще відгук</button>
        <a href="/cabinet/parent/search" class="btn btn-secondary">До пошуку нянь</a>
      </div>
    </div>
    <form class="card profile-form parent-review-form" id="parent-review-form">
      <p class="form-hint" id="review-nanny-hint">Після завершення співпраці (відкритий контакт)</p>
      <div class="form-row">
        <label class="label" for="review-nanny-select">Няня</label>
        <select class="field" id="review-nanny-select" name="nanny_id" required>
          <option value="">Оберіть няню</option>
        </select>
      </div>
      <div class="form-row">
        <span class="label">Оцінка</span>
        <div class="review-stars-input" role="group" aria-label="Оцінка">
          <button type="button">★</button><button type="button">★</button><button type="button">★</button><button type="button">★</button><button type="button">★</button>
        </div>
      </div>
      <input type="hidden" id="rating-input" value="0">
      <div class="form-row">
        <label class="label" for="review-text">Коментар</label>
        <textarea class="field" id="review-text" rows="4" placeholder="Розкажіть про досвід співпраці"></textarea>
      </div>
      <div class="profile-form-actions">
        <button type="submit" class="btn btn-primary">Надіслати відгук</button>
      </div>
    </form>
    <section class="review-suggestions" id="review-suggestions" hidden aria-label="Няні з обраного"></section>
  </div>
</div>
""", css=CAB, init=INIT)

# Nanny cabinet
page("cabinet/nanny/index.html", "Кабінет няні", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="nanny-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="nanny-nav"></nav></aside>
  <div><h1 class="cabinet-title">Дашборд</h1>
  <div class="stat-grid"><div class="card stat-card"><div class="stat-value">—</div><div class="stat-label">Рейтинг</div></div>
  <div class="card stat-card"><div class="stat-value">0</div><div class="stat-label">Відгуки</div></div>
  <div class="card stat-card"><div class="stat-value">—</div><div class="stat-label">Статус</div></div></div></div>
</div>
""", css=CAB, init=INIT)

page("cabinet/nanny/profile.html", "Профіль няні", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="nanny-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="nanny-nav"></nav></aside>
  <div class="cabinet-main nanny-profile-page">
    <div class="cabinet-page-head">
      <h1 class="cabinet-title">Профіль / Резюме</h1>
      <p class="cabinet-subtitle">Заповніть дані та додайте фото — батьки побачать профіль у каталозі після модерації</p>
    </div>
    <div class="profile-page-grid">
      <form class="card profile-form" id="nanny-profile-form">
        <div class="profile-photo-section">
          <div class="profile-avatar-wrap" id="profile-avatar-wrap">
            <img class="profile-avatar-img" id="profile-photo-preview" alt="" width="112" height="112" hidden>
            <span class="profile-avatar-fallback" id="profile-photo-fallback" aria-hidden="true">👤</span>
          </div>
          <div class="profile-photo-actions">
            <span class="label">Фото профілю</span>
            <p class="profile-photo-hint">JPEG, PNG або WebP, до 5 МБ. Квадратне фото виглядає найкраще.</p>
            <input type="file" class="profile-photo-input" id="profile-photo-input" accept="image/jpeg,image/png,image/webp" hidden>
            <button type="button" class="btn btn-secondary profile-photo-btn" id="profile-photo-btn">Змінити фото</button>
          </div>
        </div>
        <div class="form-row form-row-2">
          <div><label class="label" for="pf-first-name">Ім'я</label><input class="field" id="pf-first-name" name="first_name" autocomplete="given-name"></div>
          <div><label class="label" for="pf-last-name">Прізвище</label><input class="field" id="pf-last-name" name="last_name" autocomplete="family-name"></div>
        </div>
        <div class="form-row form-row-2">
          <div><label class="label" for="pf-city">Місто</label><input class="field" id="pf-city" name="city" readonly></div>
          <div><label class="label" for="pf-rate">Ставка ₴/год</label><input type="number" class="field" id="pf-rate" name="hourly_rate" min="0" step="10" inputmode="numeric"></div>
        </div>
        <div class="form-row">
          <label class="label" for="pf-description">Опис</label>
          <textarea class="field" id="pf-description" rows="5" name="description" placeholder="Розкажіть про досвід, підхід до дітей та сильні сторони"></textarea>
        </div>
        <div class="form-row form-row-2">
          <div><label class="label" for="pf-experience">Роки досвіду</label><input type="number" class="field" id="pf-experience" name="experience_years" min="0" inputmode="numeric"></div>
        </div>
        <div class="profile-form-actions">
          <button type="submit" class="btn btn-primary">Зберегти зміни</button>
        </div>
      </form>
      <aside class="card profile-preview-card" aria-label="Превʼю профілю">
        <h2 class="profile-preview-title">Як бачать батьки</h2>
        <div id="profile-card-preview" class="profile-preview-inner"></div>
        <ul class="profile-tips-list">
          <li>Якісне фото підвищує кількість переглядів профілю</li>
          <li>Детальний опис допомагає знайти підходящу сімʼю</li>
          <li>Після збереження профіль проходить модерацію</li>
        </ul>
      </aside>
    </div>
  </div>
</div>
""", css=CAB, init=INIT)

page("cabinet/nanny/calendar.html", "Календар", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="nanny-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="nanny-nav"></nav></aside>
  <div class="cabinet-main cabinet-calendar-page">
    <div class="cabinet-page-head">
      <h1 class="cabinet-title">Календар</h1>
      <p class="cabinet-subtitle">Позначте дні, коли ви вільні, зайняті або у відпустці — батьки побачать це у каталозі</p>
    </div>
    <div class="calendar-page-grid">
      <div class="card calendar-card">
        <div id="full-calendar"></div>
        <button type="button" class="btn btn-primary btn-block calendar-save-btn" id="cal-save-btn">Зберегти календар</button>
      </div>
      <aside class="card calendar-hint-card" aria-label="Підказки">
        <h2 class="calendar-hint-title">Як користуватись</h2>
        <div class="calendar-hint-legend">
          <span><span class="legend-dot available"></span>Доступна — можете прийняти замовлення</span>
          <span><span class="legend-dot busy"></span>Зайнята — вже є домовленість</span>
          <span><span class="legend-dot vacation"></span>Відпустка — тимчасово недоступна</span>
        </div>
        <ol class="calendar-hint-list">
          <li>Оберіть статус знизу календаря</li>
          <li>Натисніть на потрібні дні</li>
          <li>Збережіть зміни перед виходом</li>
        </ol>
        <p class="calendar-hint-note">У каталозі показуються найближчі 14 днів від сьогодні.</p>
      </aside>
    </div>
  </div>
</div>
""", css=CAB + '\n  <link rel="stylesheet" href="/css/calendar.css">', init=INIT)

page("cabinet/nanny/documents.html", "Документи", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="nanny-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="nanny-nav"></nav></aside>
  <div><h1 class="cabinet-title">Документи</h1>
  <p class="cabinet-subtitle">Завантажте скани для перевірки адміністратором</p>
  <div class="card" id="doc-list"></div>
  <form class="card doc-upload-form" id="doc-upload-form">
    <div class="doc-upload-row">
      <div><label class="label">Тип документа</label>
      <select class="field" name="doc_type" required>
        <option value="passport">Паспорт (скан)</option>
        <option value="ipn">ІПН</option>
        <option value="first_aid">Сертифікат першої допомоги</option>
        <option value="medical_cert">Медичний сертифікат</option>
        <option value="education_cert">Освітній / педагогічний</option>
        <option value="criminal_record">Довідка про несудимість</option>
        <option value="other">Інший</option>
      </select></div>
      <div class="doc-file-input"><label class="doc-file-label">Обрати файл (PDF, JPG, PNG)</label>
      <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png,image/*" required></div>
    </div>
    <button type="submit" class="btn btn-primary">Завантажити</button>
  </form>
  <p class="form-hint">Доступ до файлів лише у адміністратора</p></div>
</div>
""", css=CAB, init=INIT)

page("cabinet/nanny/messages.html", "Повідомлення", "", f"""
<div class="container cabinet-chat-wrap">
  <h1 class="cabinet-title">Повідомлення</h1>
  <div class="card chat-layout"><div class="chat-list"></div>
  <div class="chat-window"><div class="chat-header">Чат</div><div class="chat-messages" id="chat-messages"></div>
  <form class="chat-input-bar" id="chat-form">{CHAT_FORM}</form></div></div></div>
""", css=CAB, init=CHAT_INIT, extra_js=CHAT_JS)

page("cabinet/nanny/rating.html", "Рейтинг", "", """
<div class="container cabinet-layout">
  <div class="cabinet-mobile-nav" id="nanny-mobile-nav"></div>
  <aside class="cabinet-sidebar"><nav class="card" id="nanny-nav"></nav></aside>
  <div><h1 class="cabinet-title">Рейтинг</h1>
  <div class="stat-grid"><div class="card stat-card"><div class="stat-value">—</div><div class="stat-label">Середня оцінка</div></div>
  <div class="card stat-card"><div class="stat-value">0</div><div class="stat-label">Відгуки</div></div></div>
  <div id="my-reviews" class="reviews-list"></div></div>
</div>
""", css=CAB, init=INIT)

# Admin
ADMIN_SHELL = """
<div class="container cabinet-layout admin-layout">
  <div class="cabinet-mobile-nav" id="admin-mobile-nav"></div>
  <aside class="cabinet-sidebar admin-sidebar"><nav class="card" id="admin-nav"></nav></aside>
  <div class="admin-main">{content}</div>
</div>
"""

page("admin/index.html", "Адмін", "", ADMIN_SHELL.format(content="""
  <h1 class="cabinet-title">Дашборд</h1>
  <p class="cabinet-subtitle">Огляд платформи «Поміч поруч»</p>
  <div class="admin-alert-grid" id="admin-alerts"></div>
  <div class="stat-grid admin-stat-grid">
    <div class="card stat-card"><div class="stat-value" data-stat="users">0</div><div class="stat-label">Користувачі</div></div>
    <div class="card stat-card"><div class="stat-value" data-stat="nannies">0</div><div class="stat-label">Няні</div></div>
    <div class="card stat-card"><div class="stat-value" data-stat="revenue">₴0</div><div class="stat-label">Дохід</div></div>
    <div class="card stat-card"><div class="stat-value" data-stat="payments">0</div><div class="stat-label">Оплат</div></div>
  </div>
  <div class="admin-quick card">
    <h2 class="admin-section-title">Швидкі дії</h2>
    <div class="admin-quick-grid">
      <a href="/admin/profiles.html" class="admin-quick-link">Модерація профілів</a>
      <a href="/admin/documents.html" class="admin-quick-link">Перевірка документів</a>
      <a href="/admin/users.html" class="admin-quick-link">Користувачі</a>
      <a id="django-admin-link" href="#" class="admin-quick-link admin-quick-link--accent" target="_blank" rel="noopener">Повна адмінка Django →</a>
    </div>
  </div>
"""), css=CSS_ADMIN, init=INIT)

page("admin/users.html", "Користувачі — Адмін", "", ADMIN_SHELL.format(content="""
  <h1 class="cabinet-title">Користувачі</h1>
  <p class="cabinet-subtitle">Керування акаунтами батьків, нянь та адмінів</p>
  <div class="admin-filters card">
    <label class="label">Роль</label>
    <select class="field" id="users-filter-role">
      <option value="">Усі</option>
      <option value="parent">Батьки</option>
      <option value="nanny">Няні</option>
      <option value="admin">Адміни</option>
    </select>
    <label class="label">Статус</label>
    <select class="field" id="users-filter-status">
      <option value="">Усі</option>
      <option value="active">Active</option>
      <option value="pending">Pending</option>
      <option value="blocked">Blocked</option>
    </select>
  </div>
  <div class="card admin-table-wrap"><table class="admin-table">
    <thead><tr><th>Email</th><th>Роль</th><th>Статус</th><th>Дії</th></tr></thead>
    <tbody></tbody>
  </table></div>
"""), css=CSS_ADMIN, init=INIT)

page("admin/profiles.html", "Модерація — Адмін", "", ADMIN_SHELL.format(content="""
  <h1 class="cabinet-title">Модерація профілів</h1>
  <p class="cabinet-subtitle">Схвалення або відхилення профілів нянь</p>
  <div class="admin-filters card">
    <label class="label">Статус</label>
    <select class="field" id="profiles-filter-status">
      <option value="pending">На модерації</option>
      <option value="approved">Схвалені</option>
      <option value="rejected">Відхилені</option>
      <option value="draft">Чернетки</option>
    </select>
  </div>
  <div class="card admin-table-wrap"><table class="admin-table">
    <thead><tr><th>Няня</th><th>Email</th><th>Місто</th><th>Ставка</th><th>Статус</th><th>Дії</th></tr></thead>
    <tbody></tbody>
  </table></div>
"""), css=CSS_ADMIN, init=INIT)

page("admin/documents.html", "Документи — Адмін", "", ADMIN_SHELL.format(content="""
  <h1 class="cabinet-title">Документи</h1>
  <p class="cabinet-subtitle">Перевірка паспортів, ІПН та сертифікатів</p>
  <div class="admin-filters card">
    <label class="label">Статус</label>
    <select class="field" id="docs-filter-status">
      <option value="pending">Очікують</option>
      <option value="approved">Схвалені</option>
      <option value="rejected">Відхилені</option>
    </select>
  </div>
  <div class="card admin-table-wrap"><table class="admin-table">
    <thead><tr><th>Няня</th><th>Тип</th><th>Файл</th><th>Дата</th><th>Дії</th></tr></thead>
    <tbody></tbody>
  </table></div>
"""), css=CSS_ADMIN, init=INIT)

page("admin/messages.html", "Повідомлення — Адмін", "", ADMIN_SHELL.format(content=f"""
  <h1 class="cabinet-title">Повідомлення</h1>
  <p class="cabinet-subtitle">Листування з нянями від імені підтримки платформи</p>
  <div class="card chat-layout"><div class="chat-list"></div>
  <div class="chat-window"><div class="chat-header">Повідомлення</div>
  <div class="chat-messages" id="chat-messages"></div>
  <form class="chat-input-bar" id="chat-form">{CHAT_FORM}</form></div></div>
"""), css=CSS_ADMIN, init=CHAT_INIT, extra_js=CHAT_JS)

page("admin/content.html", "Контент — Адмін", "", ADMIN_SHELL.format(content="""
  <h1 class="cabinet-title">Редагування текстів сайту</h1>
  <p class="cabinet-subtitle">Усі тексти змінюються у Django Admin → розділ «Тексти сайту»</p>
  <div class="card admin-content-guide">
    <h2 class="admin-section-title">Де що редагувати</h2>
    <ul class="admin-guide-list">
      <li><strong>Головна, шапка, підвал, cookies</strong> — <a id="django-cms-home" href="#" target="_blank" rel="noopener">Тексти сайту</a> (окремі сторінки з підказками)</li>
      <li><strong>Оферта, політики, контакти, послуги</strong> — <a id="django-content-pages" href="#" target="_blank" rel="noopener">Статичні сторінки</a></li>
      <li><strong>FAQ</strong> — <a id="django-content-faq" href="#" target="_blank" rel="noopener">FAQ</a></li>
      <li><strong>Блог</strong> — <a id="django-content-blog" href="#" target="_blank" rel="noopener">Блог</a></li>
      <li><strong>Тарифи на сторінці послуг</strong> — <a id="django-pricing" href="#" target="_blank" rel="noopener">Тарифи</a></li>
      <li><strong>Телефон, email, SEO</strong> — <a id="django-content-settings" href="#" target="_blank" rel="noopener">Налаштування сайту</a></li>
    </ul>
    <p class="form-hint">Після збереження зміни зʼявляються на сайті протягом ~1 хвилини (або одразу після оновлення сторінки).</p>
  </div>
  <div class="admin-content-grid">
    <a id="django-cms-hero" href="#" class="card admin-content-card" target="_blank" rel="noopener">
      <span class="admin-content-icon">🏠</span><strong>Головна — Hero</strong><span>Заголовок, пошук, бейдж</span>
    </a>
    <a id="django-cms-header" href="#" class="card admin-content-card" target="_blank" rel="noopener">
      <span class="admin-content-icon">🔝</span><strong>Шапка</strong><span>Меню та кнопки</span>
    </a>
    <a id="django-cms-footer" href="#" class="card admin-content-card" target="_blank" rel="noopener">
      <span class="admin-content-icon">🔻</span><strong>Підвал</strong><span>Колонки, контакти</span>
    </a>
    <a id="django-cms-benefits" href="#" class="card admin-content-card" target="_blank" rel="noopener">
      <span class="admin-content-icon">✨</span><strong>Переваги</strong><span>4 картки на головній</span>
    </a>
  </div>
"""), css=CSS_ADMIN, init=INIT)

page("admin/finance.html", "Фінанси — Адмін", "", ADMIN_SHELL.format(content="""
  <h1 class="cabinet-title">Фінанси</h1>
  <p class="cabinet-subtitle">Останні платежі через LiqPay, WayForPay, Fondy</p>
  <div class="card admin-table-wrap"><table class="admin-table">
    <thead><tr><th>Order</th><th>Email</th><th>Тариф</th><th>Сума</th><th>Провайдер</th><th>Статус</th><th>Дата</th></tr></thead>
    <tbody></tbody>
  </table></div>
"""), css=CSS_ADMIN, init=INIT)

page("admin/analytics.html", "Аналітика — Адмін", "", ADMIN_SHELL.format(content="""
  <h1 class="cabinet-title">Аналітика</h1>
  <p class="cabinet-subtitle">Дохід та воронка користувачів</p>
  <div class="card admin-chart-card">
    <h2 class="admin-section-title">Дохід за місяці</h2>
    <div class="admin-chart" id="admin-revenue-chart"></div>
  </div>
  <div class="card admin-funnel-card">
    <h2 class="admin-section-title">Воронка</h2>
    <div id="admin-funnel"></div>
  </div>
  <div class="card">
    <h2 class="admin-section-title">Ролі користувачів</h2>
    <div id="admin-roles"></div>
  </div>
"""), css=CSS_ADMIN, init=INIT)

print("✓ Cabinet + Admin pages generated")
