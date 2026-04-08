# AI — Repositorio de herramientas IA

Colección de MCPs, agentes y skills reutilizables para Claude Code y OpenCode.

## Instalación rápida

```bash
git clone git@github.com:boraita/AI.git
cd AI
./install.sh
```

El script detecta automáticamente las herramientas instaladas (Claude Code, OpenCode) e instala y configura todos los MCPs de forma global. Pedirá las API keys necesarias la primera vez y las guarda en `.env`.

## Estructura

```
AI/
├── install.sh              # Instalador global (ejecutar tras clonar)
├── mcp/                    # Servidores MCP
│   ├── bible/              # Herramientas bíblicas y teológicas
│   │   └── amshejjinah-bible-mcp/       # scripture.api.bible + helloao + OpenBible
│   ├── wordpress/          # Integración con WordPress (próximamente)
│   └── utils/              # Utilidades generales (próximamente)
├── agents/                 # Agentes especializados (próximamente)
├── skills/                 # Skills para Claude Code (próximamente)
└── docs/                   # Documentación
```

## MCPs disponibles

### `mcp/bible/amshejjinah-bible-mcp`

| | |
|---|---|
| **Compatibilidad** | Claude Code · OpenCode |
| **Requiere** | Python 3 · API key gratuita en [scripture.api.bible](https://scripture.api.bible) |

Servidor MCP completo para consulta bíblica usando tres fuentes combinadas:
- **scripture.api.bible** — texto bíblico con cientos de traducciones
- **helloao.org** — 1000+ traducciones gratuitas sin API key
- **OpenBible.info** — ~340.000 concordancias cruzadas

**Herramientas disponibles:**
- `deep_study` — Estudio profundo unificado (español + inglés + comentario + concordancias en una sola llamada)
- `get_verse` / `get_passage` / `get_chapter` — Texto bíblico via API.Bible
- `get_verse_helloao` — Verso desde helloao.org (sin API key)
- `get_commentary` — Comentarios de 6 teólogos clásicos (Matthew Henry, Adam Clarke, John Gill, Jamieson-Fausset-Brown, Keil-Delitzsch, Tyndale)
- `get_cross_references` — Concordancias cruzadas con puntuación de relevancia
- `search_bible` — Búsqueda con fuzzy matching y filtros
- `list_bibles` / `list_helloao_translations` — Listado de traducciones disponibles
- `list_audio_bibles` / `get_audio_chapter` — Biblias en audio
- `biblia_get_passage` — Texto bíblico via Biblia API (Faithlife/Logos), incluye LEB
- `biblia_search` — Búsqueda en Biblia API con modo exacto o fuzzy
- `biblia_find_bibles` — Listado de traducciones disponibles en Biblia API

**Instalación manual** (si no usas `install.sh`):
```bash
cd mcp/bible/apibible
python3 -m venv venv && venv/bin/pip install -r requirements.txt

# Claude Code (global)
claude mcp add amshejjinah-bible-mcp -s user \
  -e API_BIBLE_KEY=tu_api_key \
  -- $(pwd)/venv/bin/python3 $(pwd)/server.py

# OpenCode — añadir a ~/.config/opencode/config.json:
# "amshejjinah-bible-mcp": {
#   "type": "local",
#   "command": ["/ruta/al/venv/bin/python3", "/ruta/al/server.py"],
#   "environment": { "API_BIBLE_KEY": "tu_api_key" },
#   "enabled": true
# }
```

### `mcp/logos/LogosBibleSoftwareMCP`

| | |
|---|---|
| **Compatibilidad** | Claude Code · OpenCode |
| **Requisito** | **macOS** + Logos Bible Software instalado en `/Applications/Logos.app` + Node.js |
| **Requiere** | API key gratuita en [api.biblia.com](https://api.biblia.com) |

Integración con Logos Bible Software a través del proyecto [robrawks/LogosBibleSoftwareMCP](https://github.com/robrawks/LogosBibleSoftwareMCP).

> **Solo macOS.** El MCP usa URL schemes y AppleScript para controlar la app de Logos. En Linux y Windows el `install.sh` lo omite automáticamente con un aviso.

**¿Qué hace si Logos está instalado?**
El `install.sh` clona el repositorio, compila el servidor Node.js y lo configura globalmente en Claude Code y OpenCode. Solo necesitas ejecutar `./install.sh` y proporcionar tu `BIBLIA_API_KEY`.

**20 herramientas disponibles:**
- Recuperar texto bíblico (LEB, KJV, ASV, DARBY, YLT, WEB)
- Abrir pasajes, word studies y comentarios directamente en Logos
- Buscar en el texto bíblico y obtener referencias cruzadas
- Navegar la biblioteca personal de Logos
- Acceder a notas, highlights y planes de lectura propios

## MCPs de terceros recomendados

| Nombre | Repo | Descripción | Compatibilidad |
|--------|------|-------------|----------------|
| **theologai** | [TJ-Frederick/TheologAI](https://github.com/TJ-Frederick/TheologAI) | Comentarios, léxicos griego/hebreo, textos clásicos, concordancias | Claude Code · OpenCode |
| **kairos_codex** | [batson-j/kairos_codex_mcp_server](https://github.com/batson-j/kairos_codex_mcp_server) | Traducciones vía bible.helloao.org | Claude Code · OpenCode |

## Añadir un nuevo MCP

1. Crea la carpeta `mcp/<categoria>/<nombre>/`
2. Añade `server.py` (o el entrypoint) y `requirements.txt` / `package.json`
3. Añade un bloque en `install.sh` siguiendo la estructura de los existentes, indicando en el comentario `# Targets:` para qué IAs es compatible
4. Documenta el MCP en este README con la tabla de compatibilidad
