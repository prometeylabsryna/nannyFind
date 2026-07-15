#!/usr/bin/env bash
# Видача Let's Encrypt сертифікатів (certbot --standalone, на ХОСТІ) і перехід
# nginx-контейнера з bootstrap (HTTP) на prod (HTTPS) конфіг.
#
# Перед запуском ОБОВ'ЯЗКОВО:
#   1) DNS A-записи pomich-poruch.com.ua / www / api.pomich-poruch.com.ua → IP Droplet, propagation завершено;
#   2) сайт уже відкривається по HTTP (bootstrap deploy пройшов успішно).
#
# Використання: bash deploy/scripts/init-ssl.sh you@example.com
set -euo pipefail

EMAIL="${1:-}"
if [ -z "$EMAIL" ]; then
  echo "Використання: bash deploy/scripts/init-ssl.sh admin@pomich-poruch.com.ua" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

DOMAIN="pomich-poruch.com.ua"
WWW_DOMAIN="www.pomich-poruch.com.ua"
API_DOMAIN="api.pomich-poruch.com.ua"

if ! command -v certbot >/dev/null 2>&1; then
  echo "==> Встановлюю certbot"
  apt-get update -y
  apt-get install -y certbot
fi

echo "==> Зупиняю nginx-контейнер, щоб звільнити порт 80 для certbot --standalone"
docker compose -f docker-compose.prod.yml -f docker-compose.ssl-bootstrap.yml stop nginx 2>/dev/null || true

echo "==> Видача сертифіката для ${DOMAIN}, ${WWW_DOMAIN}, ${API_DOMAIN}"
certbot certonly --standalone \
  -d "$DOMAIN" -d "$WWW_DOMAIN" -d "$API_DOMAIN" \
  --agree-tos -m "$EMAIL" --non-interactive

echo "==> Сертифікат видано. Перемикаю nginx на HTTPS-конфіг (docker-compose.prod.yml, без bootstrap)"
docker compose -f docker-compose.prod.yml up -d --build nginx

echo "==> Перевірка:"
sleep 3
curl -skI "https://${DOMAIN}/" | head -5 || true
curl -skI "https://${API_DOMAIN}/healthz/" | head -5 || true

cat <<'EOF'

==> Автопродовження сертифіката (додай у crontab -e на хості):
0 3 * * * certbot renew --pre-hook "docker compose -f /var/www/pomich-poruch/docker-compose.prod.yml stop nginx" --post-hook "docker compose -f /var/www/pomich-poruch/docker-compose.prod.yml up -d nginx" >> /var/log/certbot-renew.log 2>&1
EOF
