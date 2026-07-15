# Образ nginx: статичний фронтенд (HTML/CSS/JS) + reverse-proxy до Django.
# Build context — КОРІНЬ репозиторію (не backend/), бо тут лежить фронтенд.
FROM nginx:1.27-alpine

RUN rm -f /etc/nginx/conf.d/default.conf

# Статичний фронтенд копіюється явним списком — жодних backend/, scripts/,
# .env, .git тощо не потрапляє в образ (на відміну від volume-mount кореня).
WORKDIR /var/www/pomich-poruch

COPY index.html contacts.html cookie-policy.html faq.html favicon.ico \
     forgot-password.html how-it-works.html login.html privacy-policy.html \
     public-offer.html register.html reset-password.html services.html \
     terms-of-service.html ./
COPY admin/ ./admin/
COPY blog/ ./blog/
COPY cabinet/ ./cabinet/
COPY city/ ./city/
COPY css/ ./css/
COPY images/ ./images/
COPY js/ ./js/
COPY nanny/ ./nanny/
COPY partials/ ./partials/

WORKDIR /
