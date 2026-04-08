#!/usr/bin/env bash
# =============================================================================
# AI MCP — Instalador global
# Configura todos los MCPs del repositorio para Claude Code y OpenCode
# =============================================================================

set -euo pipefail

AI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
OPENCODE_CONFIG="$HOME/.config/opencode/config.json"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }
section() { echo -e "\n${BLUE}══════════════════════════════════════${NC}"; echo -e "${BLUE}  $*${NC}"; echo -e "${BLUE}══════════════════════════════════════${NC}"; }

# =============================================================================
# DETECCIÓN DE HERRAMIENTAS
# =============================================================================
section "Detectando herramientas instaladas"

HAS_CLAUDE=false
HAS_OPENCODE=false
HAS_PYTHON=false

command -v claude    &>/dev/null && HAS_CLAUDE=true    && ok "Claude Code encontrado"    || warn "Claude Code no encontrado"
command -v opencode  &>/dev/null && HAS_OPENCODE=true  && ok "OpenCode encontrado"       || warn "OpenCode no encontrado"
[ -f "$OPENCODE_CONFIG" ]        && HAS_OPENCODE=true  && ok "OpenCode config encontrado"
command -v python3   &>/dev/null && HAS_PYTHON=true    && ok "Python3 encontrado"        || warn "Python3 no encontrado"

# =============================================================================
# API KEYS
# =============================================================================
section "Configuración de API Keys"

# API.Bible key
if [ -z "${API_BIBLE_KEY:-}" ]; then
    if [ -f "$AI_DIR/.env" ]; then
        source "$AI_DIR/.env"
        ok "API_BIBLE_KEY cargada desde .env"
    else
        warn "API_BIBLE_KEY no encontrada"
        echo -e "  Obtén una clave gratuita en: https://scripture.api.bible"
        echo -n "  Introduce tu API_BIBLE_KEY (o Enter para omitir): "
        read -r API_BIBLE_KEY
        if [ -n "$API_BIBLE_KEY" ]; then
            echo "API_BIBLE_KEY=$API_BIBLE_KEY" > "$AI_DIR/.env"
            ok "API_BIBLE_KEY guardada en $AI_DIR/.env"
        else
            warn "Omitiendo amshejjinah-bible-mcp MCP (sin API key)"
        fi
    fi
fi

# =============================================================================
# MCP: amshejjinah-bible-mcp
# Targets: Claude Code, OpenCode
# =============================================================================
section "MCP: amshejjinah-bible-mcp  [Claude Code | OpenCode]"

MCP_BIBLE_DIR="$AI_DIR/mcp/bible/amshejjinah-bible-mcp"
MCP_BIBLE_PYTHON="$MCP_BIBLE_DIR/venv/bin/python3"

if [ "$HAS_PYTHON" = true ]; then
    info "Instalando dependencias Python..."
    cd "$MCP_BIBLE_DIR"
    python3 -m venv venv
    venv/bin/pip install -q -r requirements.txt
    ok "Dependencias instaladas en $MCP_BIBLE_DIR/venv"
    cd "$AI_DIR"

    if [ -n "${API_BIBLE_KEY:-}" ]; then

        # ── Claude Code ──────────────────────────────────────────────────────
        if [ "$HAS_CLAUDE" = true ]; then
            info "Configurando para Claude Code (global)..."
            claude mcp remove amshejjinah-bible-mcp -s user 2>/dev/null || true
            claude mcp add amshejjinah-bible-mcp -s user \
                -e API_BIBLE_KEY="$API_BIBLE_KEY" \
                -- "$MCP_BIBLE_PYTHON" "$MCP_BIBLE_DIR/server.py"
            ok "amshejjinah-bible-mcp → Claude Code (usuario global)"
        fi

        # ── OpenCode ─────────────────────────────────────────────────────────
        if [ "$HAS_OPENCODE" = true ] || [ -f "$OPENCODE_CONFIG" ]; then
            info "Configurando para OpenCode..."
            python3 - <<PYEOF
import json, os

config_path = os.path.expanduser("$OPENCODE_CONFIG")
with open(config_path, "r") as f:
    config = json.load(f)

config.setdefault("mcp", {})
config["mcp"]["amshejjinah-bible-mcp"] = {
    "type": "local",
    "command": ["$MCP_BIBLE_PYTHON", "$MCP_BIBLE_DIR/server.py"],
    "environment": {
        "API_BIBLE_KEY": "$API_BIBLE_KEY"
    },
    "enabled": True
}

with open(config_path, "w") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF
            ok "amshejjinah-bible-mcp → OpenCode"
        fi

    else
        warn "amshejjinah-bible-mcp omitido (falta API_BIBLE_KEY)"
    fi
else
    warn "amshejjinah-bible-mcp omitido (Python3 no disponible)"
fi

# =============================================================================
# AÑADIR NUEVOS MCPs AQUÍ
# Copia el bloque anterior y ajusta:
#   - section "MCP: nombre  [Claude Code | OpenCode | ...]"
#   - directorio, comando de instalación y configuración
# =============================================================================

# =============================================================================
# RESUMEN
# =============================================================================
section "Resumen de configuración"

echo ""
printf "%-20s %-15s %-15s\n" "MCP" "Claude Code" "OpenCode"
printf "%-20s %-15s %-15s\n" "────────────────────" "───────────────" "───────────────"

if [ -n "${API_BIBLE_KEY:-}" ] && [ "$HAS_PYTHON" = true ]; then
    CLAUDE_STATUS=$( [ "$HAS_CLAUDE" = true ] && echo "✓ instalado" || echo "— no disponible" )
    OPENCODE_STATUS=$( [ -f "$OPENCODE_CONFIG" ] && echo "✓ instalado" || echo "— no disponible" )
    printf "%-20s %-15s %-15s\n" "amshejjinah-bible-mcp" "$CLAUDE_STATUS" "$OPENCODE_STATUS"
else
    printf "%-20s %-15s %-15s\n" "amshejjinah-bible-mcp" "— omitido" "— omitido"
fi

echo ""
info "Para añadir nuevos MCPs edita este script en la sección marcada"
info "API keys guardadas en: $AI_DIR/.env  (no subir a git)"
echo ""
