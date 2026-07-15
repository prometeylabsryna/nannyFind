/* Public content from API */
window.PP = window.PP || {};

PP.renderFAQItems = (items) =>
  items
    .map(
      (f) =>
        `<div class="card faq-item"><button type="button" class="faq-trigger" aria-expanded="false"><span class="faq-question">${f.q}</span><svg class="faq-chevron" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></button><div class="faq-answer-wrap" aria-hidden="true"><div class="faq-answer">${f.a}</div></div></div>`
    )
    .join("");

PP.loadFAQ = async () => {
  const list = document.getElementById("faq-list");
  if (!list) return;
  try {
    const items = await PP.fetchFAQ();
    list.innerHTML = PP.renderFAQItems(items);
    PP.initFAQ();
  } catch {
    if (PP.useMockFallback?.() && PP.FAQ?.length) {
      list.innerHTML = PP.renderFAQItems(PP.FAQ);
      PP.initFAQ();
      return;
    }
    list.innerHTML = '<div class="card empty-state"><p>Не вдалося завантажити FAQ</p></div>';
  }
};

PP.renderBlogCards = (posts) =>
  posts
    .map(
      (p) =>
        `<a href="${PP.ROUTES.blogPost(p.slug)}" class="card card-hover blog-card">
            <img src="${p.image || ""}" alt="" loading="lazy" width="800" height="500">
            <div class="blog-card-body"><span class="badge badge-green">${p.category || ""}</span>
            <h3>${p.title}</h3><p>${p.excerpt || ""}</p></div></a>`
    )
    .join("");

PP.loadBlog = async () => {
  const grid = document.getElementById("blog-grid");
  if (!grid) return;
  try {
    const posts = await PP.fetchBlog();
    grid.innerHTML = posts.length
      ? PP.renderBlogCards(posts)
      : '<div class="card empty-state"><p>Статей поки немає</p></div>';
  } catch {
    if (PP.useMockFallback?.() && PP.BLOG?.length) {
      grid.innerHTML = PP.renderBlogCards(PP.BLOG);
      return;
    }
    grid.innerHTML = '<div class="card empty-state"><p>Не вдалося завантажити блог</p></div>';
  }
};

PP.loadBlogArticle = async () => {
  const root = document.getElementById("blog-article");
  const titleEl = document.getElementById("blog-article-title");
  if (!root) return;
  const slug = PP.pathBlogSlug();
  if (!slug) {
    root.innerHTML = '<div class="card empty-state"><p>Статтю не знайдено</p><a href="/blog/" class="btn btn-primary">До блогу</a></div>';
    return;
  }
  let post = null;
  try {
    post = await PP.fetchBlogPost(slug);
  } catch {
    if (PP.useMockFallback?.()) post = (PP.BLOG || []).find((b) => b.slug === slug);
  }
  if (!post) {
    root.innerHTML = '<div class="card empty-state"><p>Статтю не знайдено</p><a href="/blog/" class="btn btn-primary">До блогу</a></div>';
    return;
  }
  if (titleEl) titleEl.textContent = post.title;
  document.title = `${post.title} — Блог`;
  const img = post.image
    ? `<img src="${post.image}" alt="" class="blog-article-cover" width="800" height="450" loading="lazy">`
    : "";
  const body = Array.isArray(post.content)
    ? post.content.map((c) => `<p class="blog-article-p">${c}</p>`).join("")
    : post.body_html || post.body || "";
  root.innerHTML = `${img}<div class="blog-article-content">${body}</div>`;
};

PP.loadHomeNannies = async () => {
  const grid = document.getElementById("home-nannies");
  if (!grid) return;
  try {
    const list = await PP.fetchNannies({});
    grid.innerHTML = list.slice(0, 4).map((n) => PP.renderNannyCard(n, { compact: true })).join("");
    PP.bindChatOpenButtons?.(grid);
    PP.syncFavoriteButtons?.(grid);
  } catch {
    /* mock init in page */
  }
};

PP.loadCities = async () => {
  try {
    const cities = await PP.fetchCities();
    PP.CITIES = cities.map((c) => c.name);
    PP.DISTRICTS = {};
    cities.forEach((c) => {
      PP.DISTRICTS[c.name] = (c.districts || []).map((d) => d.name);
    });
  } catch {
    /* keep mock */
  }
};

PP.initCityPage = async (cityName) => {
  const grid = document.getElementById("city-grid");
  if (!grid) return;
  const locative = PP.cityLocative?.(cityName) || `у ${cityName}`;
  document.title = `Няні ${locative} — Поміч поруч`;
  const titleEl = document.querySelector(".page-hero-title");
  if (titleEl) titleEl.textContent = `Няні ${locative}`;
  const meta = document.querySelector('meta[name="description"]');
  if (meta) meta.setAttribute("content", `Перевірені няні ${locative}. Безпечний пошук та швидкий підбір.`);

  const render = (list) => {
    const countEl = document.getElementById("city-count");
    if (countEl) countEl.textContent = list.length || "0";
    if (!list.length) {
      grid.innerHTML = `<div class="card empty-state"><p>Нянь у цьому місті поки немає</p><a href="/nanny/" class="btn btn-primary">Увесь каталог</a></div>`;
      return;
    }
    grid.innerHTML = list.map((n) => PP.renderNannyCard(n)).join("");
    PP.bindChatOpenButtons?.(grid);
    PP.syncFavoriteButtons?.(grid);
  };

  try {
    const list = await PP.fetchNannies({ city: cityName });
    render(list);
  } catch {
    const list = (PP.NANNIES || []).filter((n) => n.city === cityName);
    render(list.map(PP.normalizeNanny));
  }
};
