#!/usr/bin/env bash
# Enciende auth (8002), account (8001), transactions (8003) y el Gateway nginx (8080).
# Uso (desde la raíz del repo):  bash backend-local/start-backend.sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv-local"
BOOT="$ROOT/.uv-boot"
LOGS="/tmp/finanzas-logs"; mkdir -p "$LOGS"
SUDO=""; [ "$(id -u)" != "0" ] && SUDO="sudo"

bash "$ROOT/backend-local/stop-backend.sh" >/dev/null 2>&1

# El backend necesita Python 3.11 (igual que sus Dockerfile). Con Python 3.13/3.14 no compila.
if [ -d "$VENV" ] && ! "$VENV/bin/python" --version 2>/dev/null | grep -q "3\.11"; then
  echo ">> Recreando el entorno con Python 3.11..."
  rm -rf "$VENV"
fi
if [ ! -d "$VENV" ]; then
  echo ">> Preparando Python 3.11 e instalando librerías (2-3 min, solo la primera vez)..."
  python3 -m venv "$BOOT" || exit 1
  "$BOOT/bin/pip" install -q uv || exit 1
  "$BOOT/bin/uv" venv --python 3.11 "$VENV" || exit 1
  "$BOOT/bin/uv" pip install -q --python "$VENV/bin/python" \
    fastapi==0.115.0 "uvicorn[standard]==0.30.6" sqlmodel==0.0.22 \
    pydantic==2.9.2 "pydantic[email]==2.9.2" "python-jose[cryptography]==3.3.0" \
    "passlib[argon2,bcrypt]==1.7.4" httpx==0.27.2 python-multipart==0.0.9 \
    || { rm -rf "$VENV"; echo "!! Falló la instalación"; exit 1; }
fi

if ! command -v nginx >/dev/null; then
  echo ">> Instalando nginx..."
  $SUDO apt-get update -q >/dev/null && $SUDO apt-get install -y -q nginx-light >/dev/null || exit 1
fi

export SECRET_KEY="clave-local-de-desarrollo-kaibacorp"
export ACCOUNT_SERVICE_URL="http://localhost:8001"
DATA="$ROOT/backend-local/data"; mkdir -p "$DATA"

arrancar() {
  ( cd "$ROOT/Backend/$2" && DATABASE_URL="sqlite:///$DATA/$1.sqlite3" \
    nohup "$VENV/bin/uvicorn" app.main:app --port "$3" >"$LOGS/$1.log" 2>&1 & echo $! >"$LOGS/$1.pid" )
  echo ">> $1 en el puerto $3"
}
arrancar account account-service 8001
arrancar auth auth-service 8002
arrancar transactions transaction-service 8003

if $SUDO nginx -c "$ROOT/backend-local/nginx.conf" 2>"$LOGS/nginx.log"; then
  echo ">> Gateway (nginx) en el puerto 8080"
else
  echo "!! El Gateway no arrancó. Mira: cat $LOGS/nginx.log"
fi

echo ">> Esperando a que los servicios respondan..."
for i in $(seq 1 30); do
  if curl -sf localhost:8080/health-auth >/dev/null && curl -sf localhost:8080/health-cuentas >/dev/null; then
    echo "LISTO: todo funciona. Gateway en el puerto 8080."
    exit 0
  fi
  sleep 1
done
echo "!! Algo no respondió. Mira los registros:"
for f in "$LOGS"/*.log; do echo "== $f"; tail -5 "$f"; done
exit 1
