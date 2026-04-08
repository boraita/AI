#!/usr/bin/env bash
# =============================================================================
# AI MCP — Instalador global
# Configura todos los MCPs del repositorio para Claude Code y OpenCode
# =============================================================================

set -euo pipefail

AI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCODE_CONFIG="$HOME/.config/opencode/config.json"
OS="$(uname)"

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
# DETECCIÓN DE HERRAMIENTAS Y SISTEMA
# =============================================================================
section "Detectando herramientas instaladas"

HAS_CLAUDE=false
HAS_OPENCODE=false
HAS_PYTHON=false
HAS_NODE=false
HAS_LOGOS=false

command -v claude    &>/dev/null && HAS_CLAUDE=true    && ok "Claude Code encontrado"    || warn "Claude Code no encontrado"
command -v opencode  &>/dev/null && HAS_OPENCODE=true  && ok "OpenCode encontrado"       || warn "OpenCode no encontrado"
[ -f "$OPENCODE_CONFIG" ]        && HAS_OPENCODE=true  && ok "OpenCode config encontrado"
command -v python3   &>/dev/null && HAS_PYTHON=true    && ok "Python3 encontrado"        || warn "Python3 no encontrado"
command -v node      &>/dev/null && HAS_NODE=true      && ok "Node.js encontrado"        || warn "Node.js no encontrado"

# Detectar Logos (solo macOS)
if [ "$OS" = "Darwin" ] && [ -d "/Applications/Logos.app" ]; then
    HAS_LOGOS=true
    ok "Logos Bible Software encontrado en /Applications/Logos.app"
elif [ "$OS" = "Darwin" ]; then
    warn "Logos Bible Software no encontrado en /Applications/Logos.app"
else
    info "Sistema: $OS — Logos MCP solo disponible en macOS"
fi

# =============================================================================
# API KEYS
# =============================================================================
section "Configuración de API Keys"

# Cargar .env si existe
[ -f "$AI_DIR/.env" ] && source "$AI_DIR/.env" && ok "API keys cargadas desde .env"

# API.Bible key
if [ -z "${API_BIBLE_KEY:-}" ]; then
    warn "API_BIBLE_KEY no encontrada"
    echo -e "  Obtén una clave gratuita en: https://scripture.api.bible"
    echo -n "  Introduce tu API_BIBLE_KEY (o Enter para omitir): "
    read -r API_BIBLE_KEY
fi

# Biblia API key (Faithlife/Logos)
if [ -z "${BIBLIA_API_KEY:-}" ]; then
    warn "BIBLIA_API_KEY no encontrada"
    echo -e "  Obtén una clave gratuita en: https://api.biblia.com"
    echo -n "  Introduce tu BIBLIA_API_KEY (o Enter para omitir): "
    read -r BIBLIA_API_KEY
fi

# Guardar keys en .env
{
    [ -n "${API_BIBLE_KEY:-}" ]  && echo "API_BIBLE_KEY=$API_BIBLE_KEY"
    [ -n "${BIBLIA_API_KEY:-}" ] && echo "BIBLIA_API_KEY=$BIBLIA_API_KEY"
} > "$AI_DIR/.env"
ok "API keys guardadas en $AI_DIR/.env"

# =============================================================================
# MCP: amshejjinah-bible-mcp
# Targets: Claude Code, OpenCode
# =============================================================================
section "MCP: amshejjinah-bible-mcp  [Claude Code | OpenCode]"

MCP_BIBLE_DIR="$AI_DIR/mcp/bible/apibible"
MCP_BIBLE_PYTHON="$MCP_BIBLE_DIR/venv/bin/python3"

BIBLE_MCP_INSTALLED=false

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
                -e BIBLIA_API_KEY="${BIBLIA_API_KEY:-}" \
                -- "$MCP_BIBLE_PYTHON" "$MCP_BIBLE_DIR/server.py"
            ok "amshejjinah-bible-mcp → Claude Code (usuario global)"
        fi

        # ── OpenCode ─────────────────────────────────────────────────────────
        if [ -f "$OPENCODE_CONFIG" ]; then
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
        "API_BIBLE_KEY": "$API_BIBLE_KEY",
        "BIBLIA_API_KEY": "${BIBLIA_API_KEY:-}"
    },
    "enabled": True
}

with open(config_path, "w") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF
            ok "amshejjinah-bible-mcp → OpenCode"
        fi

        BIBLE_MCP_INSTALLED=true
    else
        warn "amshejjinah-bible-mcp omitido (falta API_BIBLE_KEY)"
    fi
else
    warn "amshejjinah-bible-mcp omitido (Python3 no disponible)"
fi

# =============================================================================
# MCP: logos-bible-mcp
# Targets: Claude Code, OpenCode
# Requisito: macOS + Logos Bible Software instalado
# =============================================================================
section "MCP: logos-bible-mcp  [Claude Code | OpenCode]  — solo macOS"

LOGOS_MCP_DIR="$AI_DIR/mcp/logos/LogosBibleSoftwareMCP"
LOGOS_MCP_INSTALLED=false

if [ "$OS" != "Darwin" ]; then
    warn "Logos MCP omitido — solo disponible en macOS (sistema actual: $OS)"
elif [ "$HAS_LOGOS" = false ]; then
    warn "Logos MCP omitido — Logos Bible Software no encontrado en /Applications/Logos.app"
    echo -e "  Descarga Logos en: https://www.logos.com/get-started"
elif [ "$HAS_NODE" = false ]; then
    warn "Logos MCP omitido — Node.js no encontrado (necesario para compilar)"
elif [ -z "${BIBLIA_API_KEY:-}" ]; then
    warn "Logos MCP omitido — falta BIBLIA_API_KEY (requerida por Logos MCP)"
else
    info "Clonando/actualizando LogosBibleSoftwareMCP..."
    mkdir -p "$AI_DIR/mcp/logos"

    if [ -d "$LOGOS_MCP_DIR/.git" ]; then
        git -C "$LOGOS_MCP_DIR" pull --quiet
        ok "Repositorio actualizado"
    else
        git clone --quiet https://github.com/robrawks/LogosBibleSoftwareMCP.git "$LOGOS_MCP_DIR"
        ok "Repositorio clonado"
    fi

    info "Instalando dependencias y compilando..."
    cd "$LOGOS_MCP_DIR/logos-mcp-server"
    npm install --silent
    npm run build --silent
    cd "$AI_DIR"
    ok "Logos MCP compilado"

    LOGOS_ENTRY="$LOGOS_MCP_DIR/logos-mcp-server/dist/index.js"

    # ── Claude Code ──────────────────────────────────────────────────────
    if [ "$HAS_CLAUDE" = true ]; then
        info "Configurando Logos MCP para Claude Code..."
        claude mcp remove logos-bible-mcp -s user 2>/dev/null || true
        claude mcp add logos-bible-mcp -s user \
            -e BIBLIA_API_KEY="$BIBLIA_API_KEY" \
            -- node "$LOGOS_ENTRY"
        ok "logos-bible-mcp → Claude Code (usuario global)"
    fi

    # ── OpenCode ─────────────────────────────────────────────────────────
    if [ -f "$OPENCODE_CONFIG" ]; then
        info "Configurando Logos MCP para OpenCode..."
        python3 - <<PYEOF
import json, os

config_path = os.path.expanduser("$OPENCODE_CONFIG")
with open(config_path, "r") as f:
    config = json.load(f)

config.setdefault("mcp", {})
config["mcp"]["logos-bible-mcp"] = {
    "type": "local",
    "command": ["node", "$LOGOS_ENTRY"],
    "environment": {
        "BIBLIA_API_KEY": "$BIBLIA_API_KEY"
    },
    "enabled": True
}

with open(config_path, "w") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF
        ok "logos-bible-mcp → OpenCode"
    fi

    LOGOS_MCP_INSTALLED=true
fi

# =============================================================================
# AÑADIR NUEVOS MCPs AQUÍ
# Copia uno de los bloques anteriores y ajusta:
#   - section "MCP: nombre  [Claude Code | OpenCode | ...]"
#   - directorio, comando de instalación y configuración
# =============================================================================

# =============================================================================
# RESUMEN
# =============================================================================
section "Resumen de configuración"

echo ""
printf "%-30s %-18s %-18s\n" "MCP" "Claude Code" "OpenCode"
printf "%-30s %-18s %-18s\n" "──────────────────────────────" "──────────────────" "──────────────────"

# amshejjinah-bible-mcp
if [ "$BIBLE_MCP_INSTALLED" = true ]; then
    C=$( [ "$HAS_CLAUDE" = true ] && echo "✓ instalado" || echo "— no disponible" )
    O=$( [ -f "$OPENCODE_CONFIG" ] && echo "✓ instalado"  || echo "— no disponible" )
else
    C="— omitido"
    O="— omitido"
fi
printf "%-30s %-18s %-18s\n" "amshejjinah-bible-mcp" "$C" "$O"

# logos-bible-mcp
if [ "$LOGOS_MCP_INSTALLED" = true ]; then
    C=$( [ "$HAS_CLAUDE" = true ] && echo "✓ instalado" || echo "— no disponible" )
    O=$( [ -f "$OPENCODE_CONFIG" ] && echo "✓ instalado"  || echo "— no disponible" )
elif [ "$OS" != "Darwin" ]; then
    C="— solo macOS"
    O="— solo macOS"
elif [ "$HAS_LOGOS" = false ]; then
    C="— sin Logos app"
    O="— sin Logos app"
else
    C="— omitido"
    O="— omitido"
fi
printf "%-30s %-18s %-18s\n" "logos-bible-mcp" "$C" "$O"

echo ""
info "Para añadir nuevos MCPs edita este script en la sección marcada"
info "API keys guardadas en: $AI_DIR/.env  (no subir a git)"
echo ""
