#!/usr/bin/env bash
# Деплой/оновлення стеку "Поміч поруч" на DigitalOcean Droplet.
# Використання: bash deploy/scripts/deploy.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE_FILES=(-f docker-compose.prod.yml)
if [ -f /etc/letsencrypt/live/pomich-poruch.com.ua/fullchain.pem ]; then
  echo "==> SSL-сертифікат знайдено — використовую prod (HTTPS) конфіг nginx"
else
  echo "==> SSL-сертифікат ще НЕ видано — використовую bootstrap (HTTP) конфіг nginx"
  echo "    (після DNS + init-ssl.sh цей скрипт сам перейде на HTTPS)"
  COMPOSE_FILES+=(-f docker-compose.ssl-bootstrap.yml)
fi

if [ ! -f backend/.env ]; then
  echo "ПОМИЛКА: backend/.env не знайдено. Скопіюй backend/.env.example → backend/.env і заповни значення." >&2
  exit 1
fi

echo "==> Звільняю порти 80/443 від хостового nginx/apache (якщо є)"
systemctl stop nginx apache2 2>/dev/null || true
systemctl disable nginx apache2 2>/dev/null || true

echo "==> Збірка образів"
docker compose "${COMPOSE_FILES[@]}" build

echo "==> Підняття стеку"
docker compose "${COMPOSE_FILES[@]}" up -d

echo "==> Чекаю, поки backend стане healthy..."
for i in $(seq 1 30); do
  if docker compose "${COMPOSE_FILES[@]}" ps backend 2>/dev/null | grep -q "healthy"; then
    echo "==> backend healthy"
    break
  fi
  sleep 3
done

echo "==> Стан усіх сервісів:"
docker compose "${COMPOSE_FILES[@]}" ps

echo "==> Перевірка healthz зсередини мережі:"
docker compose "${COMPOSE_FILES[@]}" exec -T backend python3 -c \
  "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=5).read())"

echo "==> Готово. Логи: docker compose ${COMPOSE_FILES[*]} logs -f"
