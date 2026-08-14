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
├── skills/                 # Skills para Claude Code
│   ├── ultracode-qa/       # Auditoría QA + UX de una web entera (Workflow paralelo)
│   └── webapp-testing/     # Playwright: testing + captura pantalla-por-pantalla (fork Apache-2.0)
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

## Skills disponibles

### `skills/ultracode-qa`

| | |
|---|---|
| **Compatibilidad** | Claude Code |
| **Requiere** | Playwright (`python3 -m playwright install chromium`) |

Auditoría completa de QA + UX de una web en marcha, orquestada como "ultracode"
(un `Workflow` de agentes QA en paralelo). Actúa como QA experto que navega y
ejercita **todas** las funcionalidades, más UX experto que detecta pitfalls del
usuario, y produce un informe HTML (Artifact) ordenado por severidad. El acceso
es vía un usuario de prueba creado con el **dev-login** de la app (único toque
permitido al backend); el login normal queda fuera de alcance. Controla
colisiones aislando datos por agente y usa el modelo adecuado por tarea.

**Instalar (uso local con Claude Code):**
```bash
cp -R skills/ultracode-qa ~/.claude/skills/
```

### `skills/webapp-testing`

| | |
|---|---|
| **Compatibilidad** | Claude Code |
| **Requiere** | Playwright (`python3 -m playwright install chromium`) |
| **Licencia** | Apache-2.0 (fork del skill built-in con mejoras) |

Toolkit Playwright para interactuar y testear webapps locales. **Fork mejorado**
del skill built-in: waits robustos (no depende solo de `networkidle`, frágil en
SPA/PWA) + sección **Screen-by-Screen Capture** que audita una web/PWA pantalla
por pantalla en 4 capas (visual, árbol de accesibilidad, design tokens,
network/API) para documentarla o reconstruirla — el equivalente web de
descompilar una app móvil. Se combina con `ultracode-qa` (mecánica de
navegación) y con skills de diseño móvil (capa visual+tokens).

```bash
cp -R skills/webapp-testing ~/.claude/skills/
```

## Skills de terceros recomendados

Instalar directo desde su repo (no vendoreados aquí; licencia propia de cada uno):

| Nombre | Repo | Descripción |
|--------|------|-------------|
| **android-reverse-engineering** | [incogbyte/android-reverse-engineering-claude-skill](https://github.com/incogbyte/android-reverse-engineering-claude-skill) | Descompila APK/AAB/XAPK (jadx/vineflower), mapea pantallas, extrae endpoints, Frida en vivo. Requiere jadx, apktool, dex2jar, bundletool, frida-tools |
| **iOS-reverse-engineering** | [incogbyte/iOS-reverse-engineering-claude-skill](https://github.com/incogbyte/iOS-reverse-engineering-claude-skill) | IPA/.app, headers Obj-C/Swift, APIs, SDKs. Requiere macOS (ipsw, radare2) |
| **mobile-app-design** | [awesome-skills/mobile-app-design](https://github.com/awesome-skills/mobile-app-design) | Diseño UI/UX móvil: patrones iOS/Material 3, tokens, accesibilidad; reconstruir UI nativa |

## Añadir un nuevo MCP

1. Crea la carpeta `mcp/<categoria>/<nombre>/`
2. Añade `server.py` (o el entrypoint) y `requirements.txt` / `package.json`
3. Añade un bloque en `install.sh` siguiendo la estructura de los existentes, indicando en el comentario `# Targets:` para qué IAs es compatible
4. Documenta el MCP en este README con la tabla de compatibilidad
