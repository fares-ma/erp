#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR/frappe_docker"
COMPOSE_FILE="$COMPOSE_DIR/pwd.yml"

PORT="${ERPNEXT_PORT:-8080}"
SEED_DEMO=0
SEED_FACTORY=0
SEED_ALL=0

usage() {
  cat <<'EOF'
Digitbox Manufacturing ERP - Linux / Server Startup Script

Usage:
  ./start-erpnext.sh [OPTIONS]

Options:
  --port <PORT>     Host port to expose ERPNext on (default: 8080, or ERPNEXT_PORT env var)
  --seed-demo       Seed general commercial demo data after startup
  --seed-factory    Seed appliance factory manufacturing demo + factory users
  --seed-all        Run all seed scripts (demo + factory + factory users)
  -h, --help        Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      if [[ $# -lt 2 ]]; then
        echo "Error: --port requires a port number." >&2
        exit 1
      fi
      PORT="$2"
      shift 2
      ;;
    --seed-demo)
      SEED_DEMO=1
      shift
      ;;
    --seed-factory)
      SEED_FACTORY=1
      shift
      ;;
    --seed-all)
      SEED_ALL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: Docker CLI was not found." >&2
  echo "Install Docker on Ubuntu/Debian server with:" >&2
  echo "  curl -fsSL https://get.docker.com | sudo sh" >&2
  echo "  sudo usermod -aG docker \$USER" >&2
  exit 1
fi

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1 && sudo docker info >/dev/null 2>&1; then
    DOCKER=(sudo docker)
    echo "Using 'sudo docker' for Docker daemon access."
  else
    echo "Error: Cannot connect to Docker daemon. Ensure Docker service is running:" >&2
    echo "  sudo systemctl enable --now docker" >&2
    exit 1
  fi
fi

if ! "${DOCKER[@]}" compose version >/dev/null 2>&1; then
  echo "Error: Docker Compose v2 ('docker compose') is required." >&2
  exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Error: Could not find '$COMPOSE_FILE'." >&2
  exit 1
fi

IMAGES=(
  "redis:6.2-alpine"
  "mariadb:11.8"
  "frappe/erpnext:v16.60.0"
)

for img in "${IMAGES[@]}"; do
  if ! "${DOCKER[@]}" image inspect "$img" >/dev/null 2>&1; then
    pulled=0
    for attempt in $(seq 1 10); do
      echo "Pulling $img (attempt $attempt/10)..."
      if "${DOCKER[@]}" pull "$img"; then
        pulled=1
        break
      fi
      echo "docker pull $img failed. Retrying in 10s..." >&2
      sleep 10
    done
    if [[ "$pulled" -ne 1 ]]; then
      echo "Error: docker pull $img failed after 10 attempts." >&2
      exit 1
    fi
  fi
done

export ERPNEXT_PORT="$PORT"

echo "Starting ERPNext containers via docker compose -f pwd.yml up -d --pull never (port $ERPNEXT_PORT)..."
(
  cd "$COMPOSE_DIR"
  "${DOCKER[@]}" compose -f pwd.yml up -d --pull never
)

echo ""
echo "Current container status:"
(
  cd "$COMPOSE_DIR"
  "${DOCKER[@]}" compose -f pwd.yml ps
)

echo ""
echo "Waiting for ERPNext site setup (create-site)..."
(
  cd "$COMPOSE_DIR"
  "${DOCKER[@]}" compose -f pwd.yml logs -f create-site || true
)

echo ""
echo "Verifying http://127.0.0.1:${ERPNEXT_PORT}/api/method/ping ..."
ping_ok=0
ping_url="http://127.0.0.1:${ERPNEXT_PORT}/api/method/ping"
for p in $(seq 1 18); do
  if command -v curl >/dev/null 2>&1; then
    if resp=$(curl -fsS --max-time 10 "$ping_url" 2>/dev/null); then
      echo "ERPNext is LIVE! Response: $resp"
      ping_ok=1
      break
    fi
  elif command -v wget >/dev/null 2>&1; then
    if resp=$(wget -qO- --timeout=10 "$ping_url" 2>/dev/null); then
      echo "ERPNext is LIVE! Response: $resp"
      ping_ok=1
      break
    fi
  elif command -v python3 >/dev/null 2>&1; then
    if resp=$(python3 -c "import urllib.request; print(urllib.request.urlopen('$ping_url', timeout=10).read().decode())" 2>/dev/null); then
      echo "ERPNext is LIVE! Response: $resp"
      ping_ok=1
      break
    fi
  fi
  echo "Waiting for web server ($p/18)..."
  sleep 5
done

if [[ "$ping_ok" -ne 1 ]]; then
  echo "Warning: Containers are up, but $ping_url did not return HTTP 200 yet." >&2
  echo "Check logs with: cd \"$COMPOSE_DIR\" && ${DOCKER[*]} compose -f pwd.yml ps -a" >&2
fi

run_seed_script() {
  local script_name="$1"
  local host_path="$SCRIPT_DIR/$script_name"
  if [[ ! -f "$host_path" ]]; then
    echo "Error: Seed script '$host_path' not found." >&2
    exit 1
  fi
  echo ""
  echo "Running seed script: $script_name ..."
  (
    cd "$COMPOSE_DIR"
    "${DOCKER[@]}" compose -f pwd.yml cp "$host_path" "backend:/tmp/$script_name"
    "${DOCKER[@]}" compose -f pwd.yml exec -T backend /home/frappe/frappe-bench/env/bin/python "/tmp/$script_name"
  )
}

if [[ "$SEED_ALL" -eq 1 ]]; then
  run_seed_script "seed_demo_data.py"
  run_seed_script "seed_appliance_factory.py"
  run_seed_script "seed_factory_users_and_extras.py"
else
  if [[ "$SEED_DEMO" -eq 1 ]]; then
    run_seed_script "seed_demo_data.py"
  fi
  if [[ "$SEED_FACTORY" -eq 1 ]]; then
    run_seed_script "seed_appliance_factory.py"
    run_seed_script "seed_factory_users_and_extras.py"
  fi
fi

SERVER_IP=""
if command -v hostname >/dev/null 2>&1; then
  SERVER_IP="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
fi

echo ""
echo "============================================================"
echo "Digitbox Manufacturing ERP is ready!"
echo "  - Local URL:   http://localhost:${ERPNEXT_PORT}"
if [[ -n "$SERVER_IP" ]]; then
  echo "  - Server URL:  http://${SERVER_IP}:${ERPNEXT_PORT}"
fi
echo "  - Site:        frontend"
echo "  - Username:    Administrator"
echo "  - Password:    admin"
if [[ "$SEED_ALL" -eq 1 || "$SEED_FACTORY" -eq 1 ]]; then
  echo "  - Factory Demo Users (Password: Factory@2026):"
  echo "      gm@factory.local | stock@factory.local | production@factory.local"
  echo "      qc@factory.local | accounts@factory.local"
fi
echo "============================================================"
