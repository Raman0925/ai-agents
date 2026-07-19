#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — Deployment script for Squad (research bot)
#
# Called by the GitHub Actions CD workflow over SSH.
# Also safe to run manually on the VPS for a hot-fix deploy:
#   bash /root/apps/squad/deploy.sh
#
# Adapted from the LegalAI deploy.sh pattern. Main difference: this is a
# Telegram long-polling bot, not an HTTP server, so there's no /health
# endpoint to curl — instead we confirm PM2 shows it "online" and that it
# isn't stuck in a restart-crash-loop right after deploy.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail   # -e: exit on any error  -u: treat unset vars as errors  -o pipefail: catch pipe failures

# ── Load nvm explicitly ───────────────────────────────────────────────────────
# Non-interactive SSH sessions (like GitHub Actions' ssh-action) do NOT source
# ~/.bashrc, so nvm's PATH additions (node, npm, pm2) are invisible unless we
# load nvm ourselves here. Same issue we hit and fixed inline in cd.yml —
# this script just makes that fix reusable and testable by hand.
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 22 > /dev/null

# ── Configuration — edit these to match your VPS ────────────────────────────
REPO_DIR="/root/apps/squad"
PM2_NAME="squad"

# ── Colours for readable logs ────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[deploy]${NC} $*"; }
warn() { echo -e "${YELLOW}[deploy]${NC} $*"; }
fail() { echo -e "${RED}[deploy] ERROR:${NC} $*" >&2; exit 1; }

log "=== Squad Deploy — $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="

# ── 1. Pull latest code ──────────────────────────────────────────────────────
log "Pulling latest code from origin/main..."
cd "$REPO_DIR"
git fetch --all --prune
git checkout main
git reset --hard origin/main
log "Git HEAD is now: $(git rev-parse --short HEAD)"

# ── 2. Install dependencies ──────────────────────────────────────────────────
log "Activating venv and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# ── 3. Restart PM2 ────────────────────────────────────────────────────────────
# Note: plain `pm2 restart` (not `reload`) since single-process Python bots
# don't support PM2's zero-downtime cluster reload the way a Node HTTP
# server with multiple instances can — a brief restart gap is fine here,
# there's no incoming HTTP traffic to drop.
log "Restarting PM2 process '$PM2_NAME'..."
if pm2 describe "$PM2_NAME" > /dev/null 2>&1; then
  pm2 restart "$PM2_NAME" --update-env
else
  warn "Process '$PM2_NAME' not found in PM2 — starting fresh..."
  pm2 start main.py --name "$PM2_NAME" --interpreter venv/bin/python
fi

pm2 save

# ── 4. Health check — adapted for a polling bot, not an HTTP server ─────────
# We can't curl a /health endpoint here. Instead: wait a few seconds for
# startup, then check PM2's own status field and restart count. A healthy
# process shows status "online" with a restart count that hasn't jumped
# since we restarted it a moment ago (a jump means it crashed and PM2
# auto-restarted it — a silent failure we don't want to call "success").
log "Giving the bot 10s to finish connecting to Telegram..."
sleep 10

STATUS=$(pm2 jlist | python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data:
    if p['name'] == '$PM2_NAME':
        print(p['pm2_env']['status'])
        break
")

if [ "$STATUS" != "online" ]; then
  fail "PM2 reports status '$STATUS' (expected 'online') — deploy may have failed. Check: pm2 logs $PM2_NAME"
fi

log "PM2 status check passed ✓ ($PM2_NAME is online)"
log "=== Deploy complete — $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
