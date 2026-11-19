#!/usr/bin/env bash
SUDO=""; [ "$(id -u)" != "0" ] && SUDO="sudo"
for f in /tmp/finanzas-logs/*.pid; do [ -f "$f" ] && kill "$(cat "$f")" 2>/dev/null; done
$SUDO pkill -x nginx 2>/dev/null
$SUDO rm -f /tmp/nginx-gateway.pid /tmp/nginx-gateway-*.log
echo "Servicios detenidos"
