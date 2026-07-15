#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UID_NUM="$(id -u)"
DOMAIN="gui/$UID_NUM"
AGENTS_DIR="$HOME/Library/LaunchAgents"

mkdir -p "$AGENTS_DIR"

install_agent() {
  local label="$1"
  local src="$2"
  local dest="$AGENTS_DIR/$label.plist"

  sed "s|__ROOT__|$ROOT|g" "$src" >"$dest"
  launchctl bootout "$DOMAIN/$label" 2>/dev/null || true
  launchctl bootstrap "$DOMAIN" "$dest"
  launchctl enable "$DOMAIN/$label"
  launchctl kickstart -k "$DOMAIN/$label"
}

launchctl bootout "$DOMAIN/com.nanyfind.dev" 2>/dev/null || true
rm -f "$AGENTS_DIR/com.nanyfind.dev.plist"

"$ROOT/scripts/start_dev.sh" stop 2>/dev/null || true

install_agent "com.nanyfind.dev.frontend" "$ROOT/scripts/com.nanyfind.dev.frontend.plist"
install_agent "com.nanyfind.dev.backend" "$ROOT/scripts/com.nanyfind.dev.backend.plist"

sleep 2
"$ROOT/scripts/start_dev.sh" status
