#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="$ROOT/.run"
LOG_DIR="/tmp"
FRONTEND_PORT=8082
API_PORT=8001

export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
PYTHON="$(command -v python3)"

mkdir -p "$RUN_DIR"

port_listen_pids() {
  lsof -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null || true
}

is_running() {
  [[ -n "$(port_listen_pids "$1")" ]]
}

start_frontend() {
  local uid domain
  uid="$(id -u)"
  domain="gui/$uid"
  launchctl bootout "$domain/com.nanyfind.dev.frontend" 2>/dev/null || true
  stop_port "$FRONTEND_PORT"
  cd "$ROOT"
  nohup "$PYTHON" scripts/dev_server.py >>"$LOG_DIR/nanyfind-frontend.log" 2>&1 &
  echo $! >"$RUN_DIR/frontend.pid"
  disown
  sleep 1
  if ! pgrep -f "scripts/dev_server.py" >/dev/null; then
    echo "Помилка: dev_server не запустився. Див. $LOG_DIR/nanyfind-frontend.log"
    exit 1
  fi
}

start_backend() {
  stop_port "$API_PORT"
  cd "$ROOT/backend"
  nohup "$PYTHON" manage.py runserver "$API_PORT" >>"$LOG_DIR/nanyfind-backend.log" 2>&1 &
  echo $! >"$RUN_DIR/backend.pid"
  disown
}

stop_port() {
  local pids
  pids="$(port_listen_pids "$1")"
  if [[ -z "$pids" ]]; then
    return 0
  fi
  kill $pids 2>/dev/null || true
  sleep 1
  pids="$(port_listen_pids "$1")"
  if [[ -n "$pids" ]]; then
    kill -9 $pids 2>/dev/null || true
  fi
}

status() {
  local fe be
  if is_running "$FRONTEND_PORT"; then fe="up"; else fe="down"; fi
  if is_running "$API_PORT"; then be="up"; else be="down"; fi
  echo "Frontend ($FRONTEND_PORT): $fe"
  echo "API ($API_PORT): $be"
}

cmd="${1:-start}"
case "$cmd" in
  start)
    start_frontend
    start_backend
    sleep 3
    echo "Frontend: http://localhost:$FRONTEND_PORT"
    echo "API:      http://localhost:$API_PORT"
    set +e
    curl -s -o /dev/null -w "Status — frontend: %{http_code}, API: " "http://localhost:$FRONTEND_PORT/"
    curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:$API_PORT/healthz/"
    set -e
    ;;
  stop)
    stop_port "$FRONTEND_PORT"
    stop_port "$API_PORT"
    rm -f "$RUN_DIR/frontend.pid" "$RUN_DIR/backend.pid"
    echo "Сервери зупинено."
    ;;
  restart)
    "$0" stop
    "$0" start
    ;;
  status)
    status
    ;;
  *)
    echo "Використання: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
