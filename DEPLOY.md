# Деплой «Поміч поруч» на DigitalOcean

Домен: **pomich-poruch.com.ua**. Django-адмінка та API живуть на окремому
піддомені **api.pomich-poruch.com.ua** — головний домен уже має власну
JS-адмінку на `/admin/`, тож справжня Django-адмінка (Unfold) винесена на
піддомен, щоб шляхи не конфліктували.

## Архітектура (один Droplet, Docker Compose)

```
Інтернет
  │
  ├─ pomich-poruch.com.ua, www  ──┐
  │                                ├─► nginx (контейнер, 80/443, Let's Encrypt)
  └─ api.pomich-poruch.com.ua  ───┘        │
                                            ├─ статика сайту (вбудована в образ nginx)
                                            ├─ /api/, /ws/  → backend:8000
                                            ├─ /media/      → shared volume
                                            └─ (api-домен) / , /admin/, /static/ → backend:8000

backend (daphne, Django+DRF+Channels) ── db (PostgreSQL) ── redis (Channels layer)
```

> **Redis у чаті:** зберігає лише pub/sub і членство в group (ефемерні дані для
> WS-чату) — історія переписки лежить у Postgres. У `docker-compose.prod.yml`
> Redis навмисно обмежений: `--maxmemory 64mb --maxmemory-policy allkeys-lru`,
> persistence (RDB/AOF) вимкнено, плюс жорсткий `deploy.resources.limits.memory: 96M`
> на рівні Docker — тобто контейнер фізично не може «розповзтись» по RAM
> Droplet'а, навіть при піковому навантаженні чату.

- Фронтенд (HTML/CSS/JS, кабінети, власна JS-адмінка) — статика, вшита в образ nginx.
- Справжня Django-адмінка (Unfold), REST API, WebSocket-чат, вебхуки платіжок — усе на `api.pomich-poruch.com.ua`, проксується напряму в контейнер `backend`.
- Кнопка «Повна адмінка Django →» у власній JS-адмінці (`admin/index.html`) відкриває `api.pomich-poruch.com.ua/admin/` через одноразовий SSO-бридж (`BACKEND_URL`) — це вже реалізовано в коді, потрібні лише правильні env-змінні.

## 1. Створення Droplet

| Параметр | Значення |
|---|---|
| Image | Ubuntu 24.04 LTS x64 |
| Plan | Basic, **4 GB RAM / 2 vCPU / 80 GB SSD** (~$24/мо) — комфортно для Postgres+Redis+Django+nginx на одній машині. Мінімум прийнятний для старту — 2 GB/2 vCPU (~$18/мо), але при рості трафіку/чату варто одразу взяти 4 GB |
| Region | Frankfurt (fra1) або Amsterdam (ams3) — найкраща латентність для UA |
| Authentication | SSH-ключ (не пароль) |
| Additional | увімкнути "Monitoring"; backups — опційно, але рекомендовано (20% від ціни droplet) |

Після створення — запам'ятай публічну IP-адресу Droplet.

### Firewall (на Droplet або DO Cloud Firewall)

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

## 2. DNS-записи (робиш сам у панелі реєстратора домену)

| Тип | Host | Значення |
|---|---|---|
| A | `@` | IP Droplet |
| A | `www` | IP Droplet |
| A | `api` | IP Droplet |

Зачекай propagation (від кількох хвилин до кількох годин) — перевірити:
`dig +short pomich-poruch.com.ua`, `dig +short api.pomich-poruch.com.ua`.
Без готового DNS видача SSL-сертифікатів (крок 5) не пройде.

## 3. Підготовка сервера

```bash
ssh root@<IP_DROPLET>

# Docker
curl -fsSL https://get.docker.com | sh

# Git
apt-get update && apt-get install -y git

mkdir -p /var/www && cd /var/www
git clone <URL_РЕПОЗИТОРІЮ> pomich-poruch
cd pomich-poruch
```

> Шлях має бути `/var/www/pomich-poruch`, не вкладений `/var/www/pomich-poruch/pomich-poruch`.

## 4. Налаштування `.env`

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Розкоментуй і заповни production-блок у кінці файлу. Мінімально обов'язково:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DEBUG=False`
- `SECRET_KEY=` — згенерувати: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `ALLOWED_HOSTS=pomich-poruch.com.ua,www.pomich-poruch.com.ua,api.pomich-poruch.com.ua,backend,localhost,127.0.0.1`
- `FRONTEND_URL=https://pomich-poruch.com.ua`
- `BACKEND_URL=https://api.pomich-poruch.com.ua`
- `CORS_ALLOWED_ORIGINS=https://pomich-poruch.com.ua,https://www.pomich-poruch.com.ua`
- `CSRF_TRUSTED_ORIGINS=https://pomich-poruch.com.ua,https://www.pomich-poruch.com.ua,https://api.pomich-poruch.com.ua`
- `SECURE_SSL_REDIRECT=False` (TLS термінує nginx, Django не повинен ще раз редіректити)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — **мають збігатися** з `DB_NAME`/`DB_USER`/`DB_PASSWORD`
- `PAYMENTS_STUB_MODE=auto` (без реальних платіжних ключів — залишити; платежі працюють у тестовому/stub режимі)
- `RUN_SEED_DEMO=false` (demo-дані НЕ для продакшн)
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` — не критично, реального адміна створимо окремо (крок 7)

`RESEND_API_KEY` поки можна лишити порожнім — сайт запрацює, але лист
«скидання пароля» не надійде (лише запишеться в лог), доки не додасте
реальний API-ключ [Resend](https://resend.com) і не верифікуєте домен
(`DEFAULT_FROM_EMAIL`) через DNS (SPF/DKIM) у панелі Resend.

## 5. Перший деплой (HTTP, до SSL)

```bash
bash deploy/scripts/deploy.sh
```

Скрипт сам:
- зупиняє хостовий nginx/apache (якщо є, щоб не займали порт 80);
- збирає образи (`backend`, `nginx` з фронтендом);
- піднімає `db`, `redis`, `backend`, `nginx` (поки без SSL — `docker-compose.ssl-bootstrap.yml`, бо сертифіката ще нема);
- виконує всередині `backend` міграції + `collectstatic` (це вже налаштовано у `deploy/entrypoint.sh`);
- чекає healthcheck і показує стан усіх контейнерів.

Перевір:

```bash
curl -I http://pomich-poruch.com.ua/
curl -I http://api.pomich-poruch.com.ua/healthz/
```

Обидва мають повернути `200 OK`.

## 6. SSL (Let's Encrypt)

Коли DNS уже вказує на Droplet і HTTP-деплой працює:

```bash
bash deploy/scripts/init-ssl.sh admin@pomich-poruch.com.ua
```

Скрипт видає сертифікат одразу на 3 домени (`pomich-poruch.com.ua`,
`www.pomich-poruch.com.ua`, `api.pomich-poruch.com.ua`) через
`certbot certonly --standalone` і перемикає nginx на
`deploy/nginx/prod/default.conf` (HTTPS + redirect з 80).

Перевір:

```bash
curl -I https://pomich-poruch.com.ua/
curl -I https://api.pomich-poruch.com.ua/healthz/
curl -I https://api.pomich-poruch.com.ua/admin/login/
```

В кінці скрипт виводить рядок для `crontab -e` на хості — додай його, щоб
сертифікат сам оновлювався (Let's Encrypt діє 90 днів).

## 7. Створення реального адміна Django

```bash
docker compose -f docker-compose.prod.yml exec backend python3 manage.py createsuperuser
```

Введи email (це `USERNAME_FIELD`), username, пароль. Після цього:

- Django-адмінка: `https://api.pomich-poruch.com.ua/admin/` (логін напряму, або через кнопку «Повна адмінка Django →» у власній `/admin/` панелі на головному домені — SSO-бридж уже реалізований у `apps/accounts/admin_sso.py`, працює автоматично, якщо `BACKEND_URL` вказано правильно);
- Власна JS-адмінка: `https://pomich-poruch.com.ua/admin/` (доступна користувачу з `role=admin` / `is_staff`).

Базові довідники (міста, тарифні плани, FAQ) на старті бажано заповнити
вручну через Django-адмінку. Якщо хочете одразу набір демо-довідників —
можна разово запустити `seed_demo` (створить і фейкові профілі нянь, тому
для реального продакшн-запуску не рекомендується без подальшого очищення):

```bash
docker compose -f docker-compose.prod.yml exec backend python3 manage.py seed_demo
```

## 8. Чеклист перед публічним запуском

- [ ] `backend/.env` на сервері, **не в git** (перевірено `.gitignore`)
- [ ] `DEBUG=False`, `SECURE_SSL_REDIRECT=False` (TLS у nginx)
- [ ] `ALLOWED_HOSTS` містить обидва домени + `backend`
- [ ] `https://pomich-poruch.com.ua/` — головна сторінка, статика (`/css/`, `/js/`) віддається
- [ ] `https://pomich-poruch.com.ua/register`, `/login`, `/cabinet/parent/`, `/cabinet/nanny/` — відкриваються
- [ ] `https://api.pomich-poruch.com.ua/admin/` — Django-логін, тема Unfold, статика адмінки завантажується
- [ ] `https://api.pomich-poruch.com.ua/healthz/` → `200 {"status":"ok",...}`
- [ ] Реєстрація → логін → JWT працює (`/api/v1/auth/...`)
- [ ] WebSocket-чат підключається (`wss://pomich-poruch.com.ua/ws/...`)
- [ ] Завантаження документів/фото (media) зберігається і відкривається після рестарту контейнера
- [ ] `/media/chat/...` напряму (без токена) повертає 404 — приватні вкладення чату не публічні
- [ ] Платежі у stub-режимі: чекаут → `stub confirm` → підписка активується
- [ ] `ufw`/DO Firewall: відкриті лише 22, 80, 443
- [ ] Backup PostgreSQL налаштовано (крок нижче)
- [ ] `git status` на сервері чистий (жодних ручних правок tracked-файлів)

## Оновлення на сервері (після кожного `git push`)

**Правило:** усі зміни nginx/compose/settings — тільки через git, ніяких
ручних правок на сервері (інакше `git pull` конфліктне).

```bash
cd /var/www/pomich-poruch
git pull origin main
bash deploy/scripts/deploy.sh
```

`deploy.sh` завжди робить `build` перед `up` — це важливо: без `--build`
контейнер продовжує працювати зі старим кодом, навіть якщо файли на диску
вже оновлені.

## Backup PostgreSQL (cron на хості)

```bash
mkdir -p /var/backups/pomich-poruch
crontab -e
```

Додати:

```
0 3 * * * docker compose -f /var/www/pomich-poruch/docker-compose.prod.yml exec -T db pg_dump -U pomich pomich_poruch | gzip > /var/backups/pomich-poruch/db-$(date +%F).sql.gz
0 4 * * 0 find /var/backups/pomich-poruch -name '*.sql.gz' -mtime +30 -delete
```

## Типові проблеми

| Симптом | Причина | Фікс |
|---|---|---|
| 502 Bad Gateway | `backend` ще стартує / migrate падає | `docker compose -f docker-compose.prod.yml logs backend` |
| Django-адмінка відкривається замість власної JS-адмінки (чи навпаки) | Заплутані `ALLOWED_HOSTS`/`BACKEND_URL` | `BACKEND_URL` має бути `https://api.pomich-poruch.com.ua`, не головний домен |
| Static 404 на `/api.../admin/` | nginx `alias` ≠ `STATIC_ROOT`, або не було `collectstatic` | перевір, що `backend` контейнер відпрацював `collectstatic` (лог entrypoint) |
| CSRF 403 у Django-адмінці | `CSRF_TRUSTED_ORIGINS` без `https://api.pomich-poruch.com.ua` | додати домен з `https://` |
| certbot fails: `Problem binding to port 80` | nginx-контейнер зайняв 80 | `docker compose -f docker-compose.prod.yml -f docker-compose.ssl-bootstrap.yml stop nginx` перед `init-ssl.sh` |
| HTTPS не працює, HTTP ОК | Забули перемкнутись з `docker-compose.ssl-bootstrap.yml` на звичайний `docker-compose.prod.yml` | `docker compose -f docker-compose.prod.yml up -d --build` (без bootstrap-override) |
| DB connection refused | `backend` стартував раніше `db` | вже є `depends_on: condition: service_healthy` — перевір `docker compose logs db` |
| Зміни `.py`/`requirements.txt` не діють після деплою | `up -d` без `--build` | завжди `deploy.sh` (робить build) |
| Лист «скидання пароля» не приходить | `RESEND_API_KEY` не заданий або домен не верифікований | додати ключ Resend у `.env` і верифікувати домен (SPF/DKIM) у панелі Resend |

## Пов'язані файли

| Файл | Призначення |
|---|---|
| `docker-compose.prod.yml` | основний prod-стек (db, redis, backend, nginx) |
| `docker-compose.ssl-bootstrap.yml` | override для HTTP-етапу до видачі сертифіката |
| `deploy/nginx/Dockerfile` | образ nginx зі статикою фронтенду (без backend/, .env, .git) |
| `deploy/nginx/http/default.conf` | HTTP-only конфіг (bootstrap) |
| `deploy/nginx/prod/default.conf` | HTTPS-конфіг (обидва домени + redirect) |
| `deploy/scripts/deploy.sh` | build+up+healthcheck |
| `deploy/scripts/init-ssl.sh` | видача Let's Encrypt + перехід на HTTPS |
| `backend/.env.example` | шаблон усіх env-змінних (dev + prod-блок) |
