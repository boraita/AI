# apibible MCP

Servidor MCP unificado para estudio bíblico. Integra tres fuentes:

| Fuente | Uso |
|--------|-----|
| [scripture.api.bible](https://scripture.api.bible) | Texto en español (RVR, NVI...) y 2500+ traducciones |
| [bible.helloao.org](https://bible.helloao.org) | 1000+ traducciones gratuitas + 6 comentarios clásicos |
| [openbible.info](https://openbible.info) | ~340.000 concordancias cruzadas |

## Herramientas

### Estudio unificado
- `deep_study(verse_id)` — Versículo en español + inglés + comentario + concordancias en una sola llamada

### API.Bible
- `list_bibles(language)` — Lista traducciones (usa `spa`, `eng`, `heb`, `grc`)
- `get_bible(bible_id)` — Detalles de una traducción
- `list_books(bible_id)` — Libros de una traducción
- `get_book(bible_id, book_id)` — Detalles de un libro
- `list_chapters(bible_id, book_id)` — Capítulos de un libro
- `get_chapter(bible_id, chapter_id)` — Texto completo de un capítulo
- `list_verses(bible_id, chapter_id)` — Lista versículos de un capítulo
- `get_verse(bible_id, verse_id)` — Versículo específico
- `get_passage(bible_id, passage_id)` — Rango de versículos
- `list_sections_by_book/chapter` — Secciones con título
- `get_section(bible_id, section_id)` — Texto de una sección
- `search_bible(bible_id, query)` — Búsqueda con fuzzy matching y paginación
- `list_audio_bibles(language)` — Biblias en audio
- `get_audio_chapter(audio_bible_id, chapter_id)` — URL de audio de un capítulo

### helloao.org
- `get_verse_helloao(translation, verse_id)` — Versículo en 1000+ traducciones
- `list_helloao_translations(language)` — Lista traducciones disponibles
- `get_commentary(verse_id, commentator)` — Comentario clásico

  Comentaristas disponibles: `matthew-henry`, `jamieson-fausset-brown`, `adam-clarke`, `john-gill`, `keil-delitzsch`, `tyndale`

### OpenBible.info
- `get_cross_references(verse_id)` — Concordancias cruzadas con puntuación de relevancia

## IDs de libro

Formato: `GEN`, `EXO`, `LEV`, `NUM`, `DEU`, `JOS`, `JDG`, `RUT`, `1SA`, `2SA`, `1KI`, `2KI`, `PSA`, `PRO`, `ISA`, `JER`, `EZK`, `DAN`, `MAT`, `MRK`, `LUK`, `JHN`, `ACT`, `ROM`, `1CO`, `2CO`, `GAL`, `EPH`, `REV`...

## Traducciones en español (API.Bible)

| ID | Nombre |
|----|--------|
| `592420522e16049f-01` | Reina Valera 1909 |
| `48acedcf8595c754-01` | Palabra de Dios para ti |
| `b32b9d1b64b4ef29-01` | Santa Biblia en español sencillo |
| `482ddd53705278cc-02` | Versión Biblia Libre |

## Instalación

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt

claude mcp add apibible -s user \
  -e API_BIBLE_KEY=tu_api_key \
  -- $(pwd)/venv/bin/python3 $(pwd)/server.py
```

## Requisitos

- Python 3.10+
- API key gratuita en [scripture.api.bible](https://scripture.api.bible)
