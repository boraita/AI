# AI — Repositorio de herramientas IA

Colección de MCPs, agentes y skills reutilizables para Claude Code.

## Estructura

```
AI/
├── mcp/                    # Servidores MCP
│   ├── bible/              # Herramientas bíblicas y teológicas
│   ├── wordpress/          # Integración con WordPress
│   └── utils/              # Utilidades generales
├── agents/                 # Agentes especializados
│   ├── bible-study/        # Agente de estudio bíblico profundo
│   └── general/            # Agentes de propósito general
├── skills/                 # Skills para Claude Code
└── docs/                   # Documentación
```

## MCPs disponibles

### `mcp/bible/apibible`
Servidor MCP completo para scripture.api.bible + helloao.org + OpenBible.info.

**Herramientas:**
- `deep_study` — Estudio profundo unificado (español + inglés + comentario + concordancias)
- `get_verse` / `get_passage` / `get_chapter` — Texto bíblico via API.Bible
- `get_commentary` — Comentarios de 6 teólogos clásicos
- `get_cross_references` — ~340.000 concordancias cruzadas
- `search_bible` — Búsqueda con fuzzy matching
- `list_audio_bibles` / `get_audio_chapter` — Biblias en audio
- Y más...

**Requisitos:** API key gratuita en [scripture.api.bible](https://scripture.api.bible)

### `mcp/wordpress/`
_(próximamente)_

## Configuración rápida

```bash
# Clonar
git clone git@github.com:boraita/AI.git

# Instalar MCP de Biblia
cd mcp/bible/apibible
python3 -m venv venv && venv/bin/pip install -r requirements.txt

# Añadir a Claude Code
claude mcp add apibible -s user \
  -e API_BIBLE_KEY=tu_api_key \
  -- $(pwd)/venv/bin/python3 $(pwd)/server.py
```
