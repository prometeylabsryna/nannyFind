#!/usr/bin/env python3
"""Генератор HTML-сторінок Поміч поруч — HTML + HTMX + JS"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEAD = """<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/images/favicon-32x32.png" type="image/png" sizes="32x32">
  <link rel="icon" href="/images/favicon-16x16.png" type="image/png" sizes="16x16">
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png" sizes="180x180">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,500;0,9..40,600;0,9..40,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/globals.css">
  {extra_css}
  <script src="https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js"></script>
</head>
<body>
  <div id="site-header" hx-get="/partials/header.html" hx-trigger="load" hx-swap="innerHTML"></div>
  <main>{body}</main>
  <div id="site-footer" hx-get="/partials/footer.html" hx-trigger="load" hx-swap="innerHTML"></div>
  <div hx-get="/partials/cookie.html" hx-trigger="load" hx-swap="innerHTML"></div>
  <script src="/js/mock-data.js"></script>
  <script src="/js/api.js"></script>
  <script src="/js/roles.js"></script>
  <script src="/js/render.js"></script>
  <script src="/js/calendar.js"></script>
  <script src="/js/datepicker.js"></script>
  <script src="/js/auth.js"></script>
  <script src="/js/cabinet-core.js"></script>
  <script src="/js/cabinet-parent.js"></script>
  <script src="/js/cabinet-nanny.js"></script>
  <script src="/js/cabinet-admin.js"></script>
  <script src="/js/payments.js"></script>
  <script src="/js/content-loader.js"></script>
  <script src="/js/site-content.js"></script>
  <script src="/js/app.js"></script>
  {extra_js}
  <script>
    document.body.addEventListener('htmx:afterSwap', function(e) {{
      PP.afterPartialSwap?.(e.detail.target);
      if (e.detail.target.id === 'site-header') PP.initLayout();
    }});
    document.addEventListener('DOMContentLoaded', async function() {{
      if (PP.loadSiteContent) await PP.loadSiteContent();
      PP.initLayout();
      PP.initCookie();
      {init}
    }});
  </script>
</body>
</html>"""

CSS_PUBLIC = """
  <link rel="stylesheet" href="/css/header.css">
  <link rel="stylesheet" href="/css/footer.css">
  <link rel="stylesheet" href="/css/hero.css">
  <link rel="stylesheet" href="/css/nanny.css">
  <link rel="stylesheet" href="/css/calendar.css">
  <link rel="stylesheet" href="/css/datepicker.css">
  <link rel="stylesheet" href="/css/auth.css">
  <link rel="stylesheet" href="/css/documents.css">
  <link rel="stylesheet" href="/css/page-decor.css">"""

PAGE_DECOR = """<div class="page-decor" aria-hidden="true">
  <div class="page-decor-dots"></div>
  <span class="page-decor-blob page-decor-blob--1"></span>
  <span class="page-decor-blob page-decor-blob--2"></span>
  <span class="page-decor-blob page-decor-blob--3"></span>
  <span class="page-decor-blob page-decor-blob--4"></span>
  <span class="page-decor-ring page-decor-ring--1"></span>
  <span class="page-decor-ring page-decor-ring--2"></span>
  <span class="page-decor-wave"></span>
  <span class="page-decor-icon page-decor-icon--shield">🛡</span>
  <span class="page-decor-icon page-decor-icon--heart">💚</span>
  <span class="page-decor-icon page-decor-icon--star">✦</span>
  <span class="page-decor-icon page-decor-icon--baby">👶</span>
  <span class="page-decor-icon page-decor-icon--home">🏠</span>
</div>"""

AUTH_PAGES = frozenset({"login.html", "register.html", "forgot-password.html", "reset-password.html"})

AUTH_TRUST = """<div class="auth-page-trust">
  <span class="auth-trust-pill">🛡 Перевірені профілі</span>
  <span class="auth-trust-pill">🔒 Захист даних</span>
  <span class="auth-trust-pill">💬 Чат у кабінеті</span>
</div>"""

PAGE_ASIDE = """<aside class="card page-aside-help">
  <h2>Потрібна допомога?</h2>
  <nav class="page-aside-links" aria-label="Корисні посилання">
    <a href="/faq.html"><span>❓</span> Часті запитання</a>
    <a href="/contacts.html"><span>✉️</span> Написати нам</a>
    <a href="/how-it-works.html"><span>📋</span> Як це працює</a>
    <a href="/nanny/"><span>🔍</span> Знайти няню</a>
  </nav>
</aside>"""

CSS_CONTACTS = CSS_PUBLIC.replace(
    '  <link rel="stylesheet" href="/css/calendar.css">',
    '  <link rel="stylesheet" href="/css/contacts.css">',
).replace('  <link rel="stylesheet" href="/css/nanny.css">\n', '')
CSS_CABINET = CSS_PUBLIC + '\n  <link rel="stylesheet" href="/css/cabinet.css">\n  <link rel="stylesheet" href="/css/payments.css">'
CSS_ADMIN = CSS_CABINET + '\n  <link rel="stylesheet" href="/css/admin.css">'


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("  +", path)


def page(path, title, desc, body, css=CSS_PUBLIC, init="", extra_js="", backdrop=True):
    if (
        backdrop
        and path != "index.html"
        and path not in AUTH_PAGES
        and not path.startswith("cabinet/")
        and not path.startswith("admin/")
    ):
        body = f'<div class="page-backdrop">{PAGE_DECOR}<div class="page-backdrop-content">{body}</div></div>'
    write(path, HEAD.format(title=title, desc=desc, body=body, extra_css=css, init=init, extra_js=extra_js))


# ── HOME ──
page("index.html", "Поміч поруч — Пошук нянь", "Маркетплейс пошуку нянь в Україні", """
<section class="hero" data-cms-section="home.hero_section_visible"><div class="hero-bg"></div><div class="container hero-grid">
  <div>
    <h1 class="hero-title" data-cms="home.hero_title_html" data-cms-html="1">Надійна <em>няня поруч</em> — для вашої родини</h1>
    <p class="hero-subtitle" data-cms="home.hero_subtitle">Знайдіть перевіреного помічника за лічені хвилини. Безпечний пошук, прозорі профілі та зручний чат.</p>
    <form class="hero-search" action="/nanny/" method="get">
      <div class="hero-search-grid">
        <div><label class="label" data-cms="home.search_city_label">🏙 Місто</label>
          <select class="field" name="city"><option value="">Оберіть місто</option>
            <option>Київ</option><option>Львів</option><option>Дніпро</option></select></div>
        <div><label class="label" data-cms="home.search_date_label">📅 Дата</label><input type="date" class="field" name="date"></div>
        <div><label class="label" data-cms="home.search_format_label">Формат</label>
          <select class="field" name="format"><option value="hourly">Погодинно</option><option value="daily">На день</option><option value="live-in">Проживання</option></select></div>
      </div>
      <button type="submit" class="btn btn-primary btn-block" style="margin-top:1rem" data-cms="home.search_submit">🔍 Знайти няню</button>
    </form>
  </div>
  <div class="hero-visual">
    <img src="https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&h=750&fit=crop" alt="Няня з дитиною" width="600" height="750" data-cms="home.hero_image_alt" data-cms-attr="alt" data-cms-src="home.hero_image">
    <div class="hero-trust"><div class="hero-trust-icon" data-cms="home.hero_trust_icon">🛡</div><div><strong style="font-size:0.875rem" data-cms="home.hero_trust_count">500+ перевірених нянь</strong><br><span style="font-size:0.75rem;color:var(--text-muted)" data-cms="home.hero_trust_cities">У 5 містах України</span></div></div>
  </div>
</div></section>
<section style="padding:4rem 0" data-cms-section="home.benefits_section_visible"><div class="container grid-4" id="benefits"></div></section>
<section style="padding:4rem 0;background:white" data-cms-section="home.steps_section_visible"><div class="container">
  <h2 class="section-title" style="text-align:center" data-cms="home.steps_title">Як це працює</h2>
  <p class="section-subtitle" style="text-align:center;margin:0 auto 2rem" data-cms="home.steps_subtitle">Чотири простих кроки</p>
  <div class="grid-4" id="steps"></div>
</div></section>
<section style="padding:4rem 0" data-cms-section="home.featured_section_visible"><div class="container">
  <h2 class="section-title" style="text-align:center" data-cms="home.featured_title">Популярні няні</h2>
  <div class="nannies-grid nannies-grid--4" id="home-nannies"></div>
  <div style="text-align:center;margin-top:1.5rem">
    <a href="/nanny/" class="btn btn-secondary" data-cms="home.featured_cta">Усі профілі</a>
  </div>
</div></section>
<section style="padding:3rem 0;background:white;text-align:center" data-cms-section="home.cities_section_visible"><div class="container">
  <h2 class="section-title" data-cms="home.cities_title">Няні у вашому місті</h2>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:0.75rem;margin-top:1rem">
    <a href="/city/kyiv.html" class="btn btn-secondary" data-cms="home.city_kyiv_label">Київ</a>
    <a href="/city/lviv.html" class="btn btn-secondary" data-cms="home.city_lviv_label">Львів</a>
    <a href="/city/dnipro.html" class="btn btn-secondary" data-cms="home.city_dnipro_label">Дніпро</a>
  </div>
</div></section>
<div class="sticky-cta"><a href="/nanny/" class="btn btn-primary btn-block" data-cms="home.sticky_cta_label">Знайти няню</a></div>
""", init="""
      PP.renderHomeBenefits?.(); PP.renderHomeSteps?.();
      PP.loadCities(); PP.loadHomeNannies();
""")

# ── CATALOG ──
page("nanny/index.html", "Каталог нянь — Поміч поруч", "Пошук нянь за фільтрами", """
<section class="page-hero"><div class="page-hero-bg"></div><div class="container page-hero-inner">
  <nav class="breadcrumbs"><a href="/">Головна</a> / <span>Каталог</span></nav>
  <h1 class="page-hero-title">Каталог нянь</h1>
  <p class="page-hero-subtitle" data-cms="catalog.catalog_subtitle">10 фільтрів: місто, район, вік, досвід, ставка, рейтинг та інше</p>
</div></section>
<div class="container" style="padding-bottom:3rem">
  <button type="button" class="btn btn-secondary filters-mobile-toggle btn-block" id="filters-toggle" data-cms="catalog.catalog_filters_toggle">Показати фільтри</button>
  <div class="card filters-mobile-panel" id="filters-mobile-panel">
    <div class="filters-panel-body" id="filters-mobile"></div>
  </div>
  <div class="catalog-layout">
    <aside class="filters-desktop">
      <div class="card filters-panel">
        <div class="filters-panel-head"><h2 data-cms="catalog.catalog_filters_title">Фільтри</h2></div>
        <div class="filters-panel-body" id="filters-desktop"></div>
      </div>
    </aside>
    <div><div class="catalog-results-header"><p id="results-count"></p></div><div class="catalog-grid" id="catalog-grid"></div></div>
  </div>
</div>
""", init="PP.initCatalog();")

page("nanny/profile.html", "Профіль няні — Поміч поруч", "Профіль помічника", """
<section class="page-hero page-hero-compact"><div class="page-hero-bg"></div><div class="container page-hero-inner">
  <nav class="breadcrumbs"><a href="/">Головна</a> / <a href="/nanny/">Каталог</a> / <span>Профіль</span></nav>
</div></section>
<div class="container" style="padding-bottom:3rem" id="profile-root"></div>
<div class="sticky-cta"><a href="#" class="btn btn-primary btn-block" id="profile-cta">Написати</a></div>
""", init="PP.initProfile();")

# City pages
CITY_LOCATIVE = {"kyiv": ("Київ", "у Києві"), "lviv": ("Львів", "у Львові"), "dnipro": ("Дніпро", "у Дніпрі")}
for slug, (name, locative) in CITY_LOCATIVE.items():
    page(f"city/{slug}.html", f"Няні {locative}", f"Перевірені няні {locative}", f"""
<section class="page-hero"><div class="page-hero-bg"></div><div class="container page-hero-inner">
  <nav class="breadcrumbs"><a href="/">Головна</a> / <a href="/nanny/">Каталог</a> / <span>{name}</span></nav>
  <h1 class="page-hero-title">Няні {locative}</h1>
</div></section>
<div class="container" style="padding-bottom:3rem"><div class="catalog-grid" id="city-grid"></div>
<a href="/nanny/?city={name}" class="btn btn-primary" style="margin-top:1.5rem">Розширений пошук</a></div>
""", init=f"PP.initCityPage('{name}');")

# Static public
page("how-it-works.html", "Як це працює", "4 кроки", """
<section class="page-hero"><div class="page-hero-bg page-hero-bg--animated"></div><div class="container page-hero-inner">
  <h1 class="page-hero-title">Як це працює</h1>
  <p class="page-hero-subtitle">Від реєстрації до домовленості</p>
</div></section>
<div class="container" style="padding:3rem 1rem"><div class="grid-4" id="hiw-steps"></div>
<div class="card hiw-cta-band">
  <a href="/register.html" class="btn btn-primary">Почати зараз</a></div></div>
""", init="document.getElementById('hiw-steps').innerHTML=PP.HOW_IT_WORKS.map(s=>'<div class=\"card step-card\"><div class=\"step-num\">'+s.step+'</div><h3>'+s.title+'</h3><p style=\"font-size:0.875rem;color:var(--text-muted)\">'+s.desc+'</p></div>').join('');")

page("faq.html", "FAQ", "Питання", f"""
<section class="page-hero page-hero-compact"><div class="page-hero-bg page-hero-bg--animated"></div><div class="container page-hero-inner">
  <h1 class="page-hero-title">Часті запитання</h1></div></section>
<div class="page-content-area">
<div class="container page-content-inner" style="max-width:52rem">
  <div id="faq-list"></div>
  {PAGE_ASIDE}
</div></div>
""", init="PP.loadFAQ();")

page("contacts.html", "Контакти — Поміч поруч", "Зв'яжіться з командою Поміч поруч", """
<section class="page-hero page-hero-compact"><div class="page-hero-bg"></div><div class="container page-hero-inner">
  <nav class="breadcrumbs" aria-label="Навігація"><a href="/">Головна</a> / <span>Контакти</span></nav>
  <h1 class="page-hero-title">Контакти</h1>
  <p class="page-hero-subtitle">Маєте питання щодо пошуку няні, реєстрації чи співпраці? Напишіть — відповімо протягом робочого дня.</p>
</div></section>
<section class="contacts-section"><div class="container contacts-layout">
  <aside class="contacts-aside">
    <div class="card contacts-card">
      <h2>Зв'язок</h2>
      <p class="contacts-lead">Команда підтримки працює з понеділка по п'ятницю та допоможе з будь-яким запитом.</p>
      <ul class="contacts-list">
        <li class="contact-item"><span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16v16H4z"/><path d="m4 7 8 6 8-6"/></svg></span>
          <div class="contact-body"><span class="contact-label">Email</span><a class="contact-value" href="mailto:info@pomich-poruch.com.ua">info@pomich-poruch.com.ua</a></div></li>
        <li class="contact-item"><span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg></span>
          <div class="contact-body"><span class="contact-label">Телефон</span><a class="contact-value" href="tel:+380441234567">+380 44 123 45 67</a></div></li>
        <li class="contact-item"><span class="contact-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></span>
          <div class="contact-body"><span class="contact-label">Графік</span><span class="contact-value">Пн–Пт, 9:00–18:00</span></div></li>
      </ul>
    </div>
    <div class="contacts-map" aria-hidden="true"><span class="contacts-map-badge">Працюємо по всій Україні</span><p class="contacts-map-cities">Київ · Львів · Дніпро · Одеса · Харків</p></div>
    <div class="contacts-quick"><a href="/faq.html" class="contacts-quick-link">Часті запитання</a><a href="/nanny/" class="contacts-quick-link">Каталог нянь</a></div>
  </aside>
  <div class="contacts-form-wrap">
    <form class="card contacts-form-card" hx-post="/partials/success.html" hx-target="#contact-result" hx-swap="innerHTML">
      <h2>Написати нам</h2>
      <p class="contacts-form-intro">Опишіть ваше питання — ми надішлемо відповідь на вказаний email.</p>
      <div id="contact-result"></div>
      <div class="contacts-form-grid">
        <div class="field-group"><label class="label" for="contact-name">Ім'я</label><input class="field" id="contact-name" name="name" type="text" placeholder="Ваше ім'я" autocomplete="name" required></div>
        <div class="field-group"><label class="label" for="contact-email">Email</label><input class="field" id="contact-email" name="email" type="email" placeholder="you@example.com" autocomplete="email" inputmode="email" required></div>
        <div class="field-group field-group--full"><label class="label" for="contact-msg">Повідомлення</label><textarea class="field" id="contact-msg" name="msg" rows="5" placeholder="Чим можемо допомогти?" required></textarea></div>
      </div>
      <button type="submit" class="btn btn-primary btn-block">Надіслати повідомлення</button>
      <p class="contacts-form-note">Надсилаючи форму, ви погоджуєтесь з <a href="/privacy-policy">політикою конфіденційності</a>.</p>
    </form>
  </div>
</div></section>
""", css=CSS_CONTACTS)

page("services.html", "Послуги", "Формати та тарифи", """
<section class="page-hero"><div class="page-hero-bg page-hero-bg--animated"></div><div class="container page-hero-inner">
  <h1 class="page-hero-title">Послуги</h1></div></section>
<div class="container" style="padding:3rem 1rem"><div class="grid-3" id="services-grid"></div>
<h2 class="section-title" style="margin-top:3rem">Тарифи</h2><div class="pricing-grid" id="pricing-grid"></div></div>
""", init="""
  document.getElementById('services-grid').innerHTML=['Погодинний догляд','Догляд на день','Няня з проживанням','Вихідні','Супровід 50–60+'].map((t,i)=>'<div class=\"card service-card\" style=\"padding:1.5rem\"><h3>'+t+'</h3><a href=\"/nanny/\" class=\"btn btn-secondary btn-block\" style=\"margin-top:1rem\">Знайти</a></div>').join('');
  document.getElementById('pricing-grid').innerHTML=PP.PRICING.map(p=>'<div class=\"card pricing-card'+(p.featured?' featured':'')+'\"><h3>'+p.title+'</h3><div class=\"pricing-price\">'+PP.formatPrice(p.price)+'</div><p style=\"font-size:0.875rem;color:var(--text-muted);flex:1\">'+p.desc+'</p><a href=\"/cabinet/parent/payments.html\" class=\"btn btn-primary btn-block\">Обрати</a></div>').join('');
""")

# Blog
page("blog/index.html", "Блог", "Статті", """
<section class="page-hero page-hero-compact"><div class="page-hero-bg page-hero-bg--animated"></div><div class="container page-hero-inner"><h1 class="page-hero-title">Блог</h1></div></section>
<div class="page-content-area">
<div class="container"><div class="grid-3" id="blog-grid"></div></div></div>
""", init="PP.loadBlog();")

for post in [
    ("yak-obraty-nyanyu", "Як обрати няню"),
    ("bezpeka-ditey", "Безпека дітей"),
]:
    page(f"blog/{post[0]}.html", post[1], post[1], f"""
<section class="page-hero page-hero-compact"><div class="page-hero-bg"></div><div class="container page-hero-inner">
  <nav class="breadcrumbs"><a href="/blog/">← Блог</a></nav>
  <h1 class="page-hero-title">{post[1]}</h1></div></section>
<article class="container" style="padding-bottom:3rem;max-width:48rem" id="blog-article" data-slug="{post[0]}"></article>
""", init="const p=PP.BLOG.find(b=>b.slug===document.getElementById('blog-article').dataset.slug); if(p) document.getElementById('blog-article').innerHTML='<img src=\"'+p.image+'\" style=\"width:100%;border-radius:1.5rem;margin-bottom:1.5rem\">'+p.content.map(c=>'<p style=\"margin-bottom:1rem;line-height:1.7\">'+c+'</p>').join('');")

# Auth
page("login.html", "Вхід", "Вхід", f"""
<div class="auth-page">{PAGE_DECOR}<div class="card auth-card">
  <h1 class="auth-title">Вхід</h1><p class="auth-subtitle">Ласкаво просимо на Поміч поруч</p>
  <div class="auth-oauth">
    <button type="button" class="auth-oauth-btn" data-provider="google">G Google</button>
    <button type="button" class="auth-oauth-btn" data-provider="facebook">f Facebook</button>
    <button type="button" class="auth-oauth-btn" data-provider="apple"> Apple</button>
  </div>
  <div class="auth-divider">або email</div>
  <form class="auth-form" id="login-form"><input class="field" type="email" placeholder="Email" required><input class="field" type="password" placeholder="Пароль" required>
  <button type="submit" class="btn btn-primary btn-block">Увійти</button></form>
  <p class="auth-footer">Немає акаунту? <a href="/register.html">Зареєструватись</a> · <a href="/forgot-password.html">Забули пароль?</a></p>
</div>{AUTH_TRUST}</div>
""", init="PP.initAuth();")

page("register.html", "Реєстрація", "Реєстрація", f"""
<div class="auth-page">{PAGE_DECOR}<div class="card auth-card auth-card-wide">
  <h1 class="auth-title">Реєстрація</h1>
  <div class="auth-role-select">
    <button type="button" class="auth-role-option active" data-role="parent">👨‍👩‍👧<br>Батьки</button>
    <button type="button" class="auth-role-option" data-role="nanny">🤝<br>Помічник</button>
  </div>
  <input type="hidden" id="role-input" value="parent">
  <div class="auth-oauth">
    <button type="button" class="auth-oauth-btn" data-provider="google">G Google</button>
    <button type="button" class="auth-oauth-btn" data-provider="facebook">f FB</button>
    <button type="button" class="auth-oauth-btn" data-provider="apple"> Apple</button>
  </div>
  <div class="auth-divider">або email</div>
  <form class="auth-form" id="register-form">
    <input class="field" name="first_name" placeholder="Ім'я" required>
    <input class="field" type="email" placeholder="Email" required>
    <input class="field" type="password" placeholder="Пароль (мін. 12 символів)" minlength="12" required>
    <div id="register-docs-panel" hidden>
      <p class="auth-docs-note">Для помічників: завантажте скани. Паспорт та ІПН обов'язкові.</p>
      <label class="label">Паспорт *</label>
      <input class="field" type="file" data-doc-type="passport" accept=".pdf,.jpg,.jpeg,.png,image/*">
      <label class="label">ІПН *</label>
      <input class="field" type="file" data-doc-type="ipn" accept=".pdf,.jpg,.jpeg,.png,image/*">
      <label class="label">Сертифікат першої допомоги</label>
      <input class="field" type="file" data-doc-type="first_aid" accept=".pdf,.jpg,.jpeg,.png,image/*">
      <label class="label">Освітній сертифікат</label>
      <input class="field" type="file" data-doc-type="education_cert" accept=".pdf,.jpg,.jpeg,.png,image/*">
    </div>
    <button type="submit" class="btn btn-primary btn-block">Створити акаунт</button>
  </form>
  <div id="register-step2" class="auth-step2" hidden></div>
  <p class="auth-footer"><a href="/login.html">Вже маю акаунт</a></p>
</div>{AUTH_TRUST}</div>
""", init="PP.initAuth(); PP.toggleRegisterDocs('parent');")

page("forgot-password.html", "Скидання пароля", "", f"""
<div class="auth-page">{PAGE_DECOR}<div class="card auth-card">
  <h1 class="auth-title">Скидання пароля</h1>
  <form class="auth-form" id="forgot-form"><input class="field" type="email" placeholder="Email" required><button type="submit" class="btn btn-primary btn-block">Надіслати посилання</button></form>
  <p class="auth-footer"><a href="/login.html">← Назад до входу</a></p>
</div>{AUTH_TRUST}</div>
""", init="PP.initAuth();")

page("reset-password.html", "Новий пароль", "Встановлення нового пароля", f"""
<div class="auth-page">{PAGE_DECOR}<div class="card auth-card">
  <h1 class="auth-title">Новий пароль</h1>
  <p class="auth-subtitle">Введіть новий пароль (мін. 12 символів)</p>
  <p class="auth-error" id="reset-error" hidden></p>
  <form class="auth-form" id="reset-form">
    <input class="field" type="password" placeholder="Новий пароль" minlength="12" required>
    <input class="field" type="password" name="password_confirm" placeholder="Підтвердіть пароль" minlength="12" required>
    <button type="submit" class="btn btn-primary btn-block">Зберегти пароль</button>
  </form>
  <p class="auth-footer"><a href="/login.html">← Назад до входу</a></p>
</div>{AUTH_TRUST}</div>
""", init="PP.initAuth();")

# Legal
for slug, title, body in [
    ("public-offer", "Публічна оферта", "<p>Публічна оферта платформи «Поміч поруч».</p><p>1 контакт — 50 грн · 5 контактів — 200 грн · Місто 7 днів — 500 грн.</p>"),
    ("terms-of-service", "Умови використання", "<p>Ролі: гість (перегляд без реєстрації), батьки, помічники, адмін. Заборонено надавати неправдиві дані.</p>"),
    ("privacy-policy", "Політика конфіденційності", "<p>GDPR та ЗУ про захист персональних даних. Документи нянь — лише для адміна.</p>"),
    ("cookie-policy", "Політика cookies", "<p>Необхідні, аналітичні (GA4, Clarity), маркетингові (Meta Pixel).</p>"),
]:
    page(f"{slug}.html", f"{title} — Поміч поруч", title, f"""
<section class="page-hero page-hero-compact"><div class="page-hero-bg page-hero-bg--animated"></div><div class="container page-hero-inner"><h1 class="page-hero-title" data-static-title>{title}</h1></div></section>
<div class="page-content-area">
<div class="container page-content-inner">
  <div class="card legal-content" data-static-body>{body}
    <div class="page-empty-hint"><span class="page-empty-hint-icon">📄</span><span>Документ оновлюється відповідно до законодавства України та GDPR.</span></div>
  </div>
  {PAGE_ASIDE}
</div></div>
""")

write("partials/success.html", '<p style="color:var(--calm-dark);font-weight:500">✓ Дякуємо! Ми отримали ваше повідомлення.</p>')

print("\n✓ Public pages generated. Run cabinet/admin generator next.")
