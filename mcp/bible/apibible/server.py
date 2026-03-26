import os
import httpx
from mcp.server.fastmcp import FastMCP

API_KEY = os.getenv("API_BIBLE_KEY", "")
BASE_URL = "https://rest.api.bible/v1"
HEADERS = {"api-key": API_KEY}

mcp = FastMCP("apibible")

CONTENT_PARAMS = {
    "content-type": "text",
    "include-verse-numbers": "true",
    "include-verse-spans": "false",
    "include-chapter-numbers": "false",
    "include-notes": "false",
    "include-titles": "true",
}


def _get(path: str, params: dict = None) -> dict:
    url = f"{BASE_URL}{path}"
    response = httpx.get(url, headers=HEADERS, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


# ── BIBLES ────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_bibles(language: str = "", abbreviation: str = "", name: str = "") -> list:
    """List available Bible translations. Filter by language, abbreviation or name.

    Args:
        language: ISO 639-3 language code (e.g. 'spa' for Spanish, 'eng' English, 'heb' Hebrew, 'grc' Greek)
        abbreviation: Bible abbreviation to search for (e.g. 'RVR09', 'KJV', 'ESV')
        name: Bible name to search for
    """
    params = {}
    if language:
        params["language"] = language
    if abbreviation:
        params["abbreviation"] = abbreviation
    if name:
        params["name"] = name
    data = _get("/bibles", params)
    return [
        {
            "id": b["id"],
            "name": b["name"],
            "language": b.get("language", {}).get("name", ""),
            "language_code": b.get("language", {}).get("id", ""),
            "abbreviation": b.get("abbreviation", ""),
            "description": b.get("description", "")
        }
        for b in data.get("data", [])
    ]


@mcp.tool()
def get_bible(bible_id: str) -> dict:
    """Get details of a specific Bible translation including copyright info.

    Args:
        bible_id: The Bible translation ID
    """
    data = _get(f"/bibles/{bible_id}")
    b = data.get("data", {})
    return {
        "id": b.get("id"),
        "name": b.get("name"),
        "abbreviation": b.get("abbreviation"),
        "language": b.get("language", {}).get("name"),
        "description": b.get("description"),
        "copyright": b.get("copyright"),
        "info": b.get("info"),
        "number_of_books": b.get("numberOfBooks"),
    }


# ── BOOKS ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_books(bible_id: str, include_chapters: bool = False) -> list:
    """List all books in a Bible translation.

    Args:
        bible_id: The Bible translation ID
        include_chapters: Whether to include chapter list for each book
    """
    params = {"include-chapters": str(include_chapters).lower()}
    data = _get(f"/bibles/{bible_id}/books", params)
    return [
        {
            "id": b["id"],
            "name": b["name"],
            "abbreviation": b.get("abbreviation", ""),
            "number_of_chapters": b.get("numberOfChapters"),
            "chapters": b.get("chapters", [])
        }
        for b in data.get("data", [])
    ]


@mcp.tool()
def get_book(bible_id: str, book_id: str) -> dict:
    """Get details of a specific book.

    Args:
        bible_id: The Bible translation ID
        book_id: Book ID (e.g. 'GEN', 'JHN', 'PSA', '2SA')
    """
    params = {"include-chapters": "true"}
    data = _get(f"/bibles/{bible_id}/books/{book_id}", params)
    b = data.get("data", {})
    return {
        "id": b.get("id"),
        "name": b.get("name"),
        "abbreviation": b.get("abbreviation"),
        "number_of_chapters": b.get("numberOfChapters"),
        "chapters": [{"id": c["id"], "number": c.get("number")} for c in b.get("chapters", [])]
    }


# ── CHAPTERS ──────────────────────────────────────────────────────────────────

@mcp.tool()
def list_chapters(bible_id: str, book_id: str) -> list:
    """List all chapters in a book.

    Args:
        bible_id: The Bible translation ID
        book_id: Book ID (e.g. 'GEN', 'JHN', 'PSA')
    """
    data = _get(f"/bibles/{bible_id}/books/{book_id}/chapters")
    return [
        {"id": c["id"], "number": c.get("number"), "reference": c.get("reference")}
        for c in data.get("data", [])
    ]


@mcp.tool()
def get_chapter(bible_id: str, chapter_id: str, include_notes: bool = False) -> dict:
    """Get the full text of a chapter.

    Args:
        bible_id: The Bible translation ID
        chapter_id: Chapter ID in format BOOKID.CHAPTER (e.g. 'JHN.3', 'GEN.1', '2SA.11', 'PSA.119')
        include_notes: Whether to include footnotes
    """
    params = {**CONTENT_PARAMS, "include-notes": str(include_notes).lower()}
    data = _get(f"/bibles/{bible_id}/chapters/{chapter_id}", params)
    c = data.get("data", {})
    return {
        "id": c.get("id"),
        "reference": c.get("reference"),
        "content": c.get("content", ""),
        "copyright": c.get("copyright", ""),
        "next": c.get("next", {}).get("id") if c.get("next") else None,
        "previous": c.get("previous", {}).get("id") if c.get("previous") else None,
    }


# ── VERSES ────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_verses(bible_id: str, chapter_id: str) -> list:
    """List all verses in a chapter (without text, just references).

    Args:
        bible_id: The Bible translation ID
        chapter_id: Chapter ID (e.g. 'JHN.3', 'GEN.1')
    """
    data = _get(f"/bibles/{bible_id}/chapters/{chapter_id}/verses")
    return [
        {"id": v["id"], "reference": v.get("reference")}
        for v in data.get("data", [])
    ]


@mcp.tool()
def get_verse(bible_id: str, verse_id: str, include_notes: bool = False) -> dict:
    """Get a specific verse with its text.

    Args:
        bible_id: The Bible translation ID
        verse_id: Verse ID in format BOOKID.CHAPTER.VERSE (e.g. 'JHN.3.16', 'GEN.1.1', '2SA.11.3')
        include_notes: Whether to include footnotes
    """
    params = {**CONTENT_PARAMS, "include-notes": str(include_notes).lower()}
    data = _get(f"/bibles/{bible_id}/verses/{verse_id}", params)
    v = data.get("data", {})
    return {
        "id": v.get("id"),
        "reference": v.get("reference"),
        "content": v.get("content", ""),
        "copyright": v.get("copyright", ""),
    }


# ── PASSAGES ──────────────────────────────────────────────────────────────────

@mcp.tool()
def get_passage(bible_id: str, passage_id: str, include_notes: bool = False) -> dict:
    """Get a passage (range of verses).

    Args:
        bible_id: The Bible translation ID
        passage_id: Passage ID format BOOKID.CHAPTER.VERSE-BOOKID.CHAPTER.VERSE (e.g. 'JHN.3.16-JHN.3.21', 'GEN.1.1-GEN.1.10')
        include_notes: Whether to include footnotes
    """
    params = {**CONTENT_PARAMS, "include-notes": str(include_notes).lower()}
    data = _get(f"/bibles/{bible_id}/passages/{passage_id}", params)
    p = data.get("data", {})
    return {
        "id": p.get("id"),
        "reference": p.get("reference"),
        "content": p.get("content", ""),
        "copyright": p.get("copyright", ""),
    }


# ── SECTIONS ──────────────────────────────────────────────────────────────────

@mcp.tool()
def list_sections_by_book(bible_id: str, book_id: str) -> list:
    """List all titled sections in a book (e.g. 'The Birth of Jesus').

    Args:
        bible_id: The Bible translation ID
        book_id: Book ID (e.g. 'MAT', 'GEN', 'PSA')
    """
    data = _get(f"/bibles/{bible_id}/books/{book_id}/sections")
    return [
        {"id": s["id"], "title": s.get("title"), "first_verse_id": s.get("firstVerseId"), "last_verse_id": s.get("lastVerseId")}
        for s in data.get("data", [])
    ]


@mcp.tool()
def list_sections_by_chapter(bible_id: str, chapter_id: str) -> list:
    """List all titled sections in a chapter.

    Args:
        bible_id: The Bible translation ID
        chapter_id: Chapter ID (e.g. 'MAT.1', 'GEN.1')
    """
    data = _get(f"/bibles/{bible_id}/chapters/{chapter_id}/sections")
    return [
        {"id": s["id"], "title": s.get("title"), "first_verse_id": s.get("firstVerseId"), "last_verse_id": s.get("lastVerseId")}
        for s in data.get("data", [])
    ]


@mcp.tool()
def get_section(bible_id: str, section_id: str) -> dict:
    """Get the full text of a titled section.

    Args:
        bible_id: The Bible translation ID
        section_id: Section ID (obtain from list_sections_by_book or list_sections_by_chapter)
    """
    data = _get(f"/bibles/{bible_id}/sections/{section_id}", CONTENT_PARAMS)
    s = data.get("data", {})
    return {
        "id": s.get("id"),
        "title": s.get("title"),
        "reference": s.get("reference"),
        "content": s.get("content", ""),
        "copyright": s.get("copyright", ""),
    }


# ── SEARCH ────────────────────────────────────────────────────────────────────

@mcp.tool()
def search_bible(bible_id: str, query: str, limit: int = 10, offset: int = 0,
                 sort: str = "relevance", range: str = "", fuzziness: str = "AUTO") -> dict:
    """Search for words or phrases in a Bible translation.

    Args:
        bible_id: The Bible translation ID
        query: Search keywords or passage reference. Supports wildcards * and ?
        limit: Maximum number of results (default 10, max 100)
        offset: Offset for pagination
        sort: Sort order: 'relevance' (default) or 'canonical'
        range: Comma-separated passage ids to restrict search (e.g. 'MAT,MRK' or 'JHN.3')
        fuzziness: Fuzziness for typo tolerance: '0', '1', '2', or 'AUTO' (default)
    """
    params = {
        "query": query,
        "limit": limit,
        "offset": offset,
        "sort": sort,
        "fuzziness": fuzziness,
    }
    if range:
        params["range"] = range
    data = _get(f"/bibles/{bible_id}/search", params)
    results = data.get("data", {})
    verses = results.get("verses", []) or []
    passages = results.get("passages", []) or []
    return {
        "total": results.get("total", 0),
        "query": query,
        "verses": [{"id": v["id"], "reference": v.get("reference", ""), "text": v.get("text", "")} for v in verses],
        "passages": [{"id": p["id"], "reference": p.get("reference", ""), "content": p.get("content", "")} for p in passages]
    }


# ── AUDIO BIBLES ──────────────────────────────────────────────────────────────

@mcp.tool()
def list_audio_bibles(language: str = "", bible_id: str = "") -> list:
    """List available audio Bible translations.

    Args:
        language: ISO 639-3 language code to filter (e.g. 'spa', 'eng')
        bible_id: Filter by related text Bible ID
    """
    params = {}
    if language:
        params["language"] = language
    if bible_id:
        params["bibleId"] = bible_id
    data = _get("/audio-bibles", params)
    return [
        {
            "id": b["id"],
            "name": b["name"],
            "language": b.get("language", {}).get("name", ""),
            "abbreviation": b.get("abbreviation", ""),
            "description": b.get("description", "")
        }
        for b in data.get("data", [])
    ]


@mcp.tool()
def get_audio_chapter(audio_bible_id: str, chapter_id: str) -> dict:
    """Get audio chapter data (URL to audio file).

    Args:
        audio_bible_id: The audio Bible ID (from list_audio_bibles)
        chapter_id: Chapter ID (e.g. 'JHN.3', 'GEN.1')
    """
    data = _get(f"/audio-bibles/{audio_bible_id}/chapters/{chapter_id}")
    c = data.get("data", {})
    return {
        "id": c.get("id"),
        "reference": c.get("reference"),
        "audio_url": c.get("resourceUrl"),
        "duration": c.get("duration"),
        "size": c.get("size"),
    }


# ── HELLOAO — COMENTARIOS Y TRADUCCIONES ──────────────────────────────────────

HELLOAO_BASE = "https://bible.helloao.org/api"

COMMENTARY_IDS = {
    "matthew-henry": "Matthew Henry",
    "jamieson-fausset-brown": "Jamieson-Fausset-Brown",
    "adam-clarke": "Adam Clarke",
    "john-gill": "John Gill",
    "keil-delitzsch": "Keil-Delitzsch (AT)",
    "tyndale": "Tyndale",
}

BOOK_MAP = {
    "GEN": "GEN", "EXO": "EXO", "LEV": "LEV", "NUM": "NUM", "DEU": "DEU",
    "JOS": "JOS", "JDG": "JDG", "RUT": "RUT", "1SA": "1SA", "2SA": "2SA",
    "1KI": "1KI", "2KI": "2KI", "1CH": "1CH", "2CH": "2CH", "EZR": "EZR",
    "NEH": "NEH", "EST": "EST", "JOB": "JOB", "PSA": "PSA", "PRO": "PRO",
    "ECC": "ECC", "SNG": "SNG", "ISA": "ISA", "JER": "JER", "LAM": "LAM",
    "EZK": "EZK", "DAN": "DAN", "HOS": "HOS", "JOL": "JOL", "AMO": "AMO",
    "OBA": "OBA", "JON": "JON", "MIC": "MIC", "NAM": "NAM", "HAB": "HAB",
    "ZEP": "ZEP", "HAG": "HAG", "ZEC": "ZEC", "MAL": "MAL",
    "MAT": "MAT", "MRK": "MRK", "LUK": "LUK", "JHN": "JHN", "ACT": "ACT",
    "ROM": "ROM", "1CO": "1CO", "2CO": "2CO", "GAL": "GAL", "EPH": "EPH",
    "PHP": "PHP", "COL": "COL", "1TH": "1TH", "2TH": "2TH", "1TI": "1TI",
    "2TI": "2TI", "TIT": "TIT", "PHM": "PHM", "HEB": "HEB", "JAS": "JAS",
    "1PE": "1PE", "2PE": "2PE", "1JN": "1JN", "2JN": "2JN", "3JN": "3JN",
    "JUD": "JUD", "REV": "REV",
}


def _helloao_get(path: str) -> dict:
    url = f"{HELLOAO_BASE}{path}"
    response = httpx.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def _parse_verse_id(verse_id: str) -> tuple[str, int, int]:
    """Parse 'JHN.3.16' → ('JHN', 3, 16)"""
    parts = verse_id.split(".")
    return parts[0], int(parts[1]), int(parts[2])


@mcp.tool()
def get_commentary(verse_id: str, commentator: str = "matthew-henry") -> dict:
    """Get commentary on a verse from classic theologians via helloao.org.

    Args:
        verse_id: Verse ID in format BOOKID.CHAPTER.VERSE (e.g. 'JHN.3.16', '2SA.11.3')
        commentator: One of: matthew-henry, jamieson-fausset-brown, adam-clarke, john-gill, keil-delitzsch, tyndale
    """
    book, chapter, verse = _parse_verse_id(verse_id)
    if commentator not in COMMENTARY_IDS:
        available = ", ".join(COMMENTARY_IDS.keys())
        return {"error": f"Unknown commentator. Available: {available}"}
    try:
        data = _helloao_get(f"/c/{commentator}/{book}/{chapter}.json")
        verses = data.get("chapter", {}).get("verses", [])
        for v in verses:
            if v.get("number") == verse:
                items = v.get("items", [])
                text = " ".join(
                    i.get("text", "") for i in items if i.get("type") == "verse"
                ).strip()
                return {
                    "reference": f"{book} {chapter}:{verse}",
                    "commentator": COMMENTARY_IDS[commentator],
                    "commentary": text or "No commentary available for this verse.",
                }
        return {"error": f"Verse {verse} not found in chapter {chapter}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_verse_helloao(translation: str, verse_id: str) -> dict:
    """Get a verse from helloao.org (1000+ free translations, no API key needed).

    Args:
        translation: Translation ID (e.g. 'WEB', 'BSB', 'KJV', 'ASV', 'RVR1909', 'NVI')
        verse_id: Verse ID in format BOOKID.CHAPTER.VERSE (e.g. 'JHN.3.16', 'GEN.1.1')
    """
    book, chapter, verse = _parse_verse_id(verse_id)
    try:
        data = _helloao_get(f"/{translation}/{book}/{chapter}.json")
        verses = data.get("chapter", {}).get("verses", [])
        for v in verses:
            if v.get("number") == verse:
                items = v.get("items", [])
                text = " ".join(
                    i.get("text", "") for i in items if i.get("type") == "verse"
                ).strip()
                return {
                    "reference": f"{book} {chapter}:{verse}",
                    "translation": translation,
                    "text": text,
                }
        return {"error": f"Verse not found"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_helloao_translations(language: str = "") -> list:
    """List available translations on helloao.org (1000+).

    Args:
        language: Filter by language name (e.g. 'Spanish', 'English', 'Hebrew', 'Greek')
    """
    data = _helloao_get("/available_translations.json")
    translations = data.get("translations", [])
    if language:
        translations = [t for t in translations if language.lower() in t.get("language", {}).get("name", "").lower()]
    return [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "language": t.get("language", {}).get("name", ""),
            "short_name": t.get("shortName", ""),
        }
        for t in translations
    ]


# ── OPENBIBLE — CONCORDANCIAS CRUZADAS ────────────────────────────────────────

@mcp.tool()
def get_cross_references(verse_id: str, min_votes: int = 10, limit: int = 10) -> list:
    """Get cross-references for a verse from OpenBible.info (~340,000 cross-references).

    Args:
        verse_id: Verse ID in format BOOKID.CHAPTER.VERSE (e.g. 'JHN.3.16', 'GEN.1.1')
        min_votes: Minimum vote score to filter quality references (default 10)
        limit: Maximum number of results (default 10)
    """
    book, chapter, verse = _parse_verse_id(verse_id)

    BOOK_OSIS = {
        "GEN":"Gen","EXO":"Exod","LEV":"Lev","NUM":"Num","DEU":"Deut","JOS":"Josh",
        "JDG":"Judg","RUT":"Ruth","1SA":"1Sam","2SA":"2Sam","1KI":"1Kgs","2KI":"2Kgs",
        "1CH":"1Chr","2CH":"2Chr","EZR":"Ezra","NEH":"Neh","EST":"Esth","JOB":"Job",
        "PSA":"Ps","PRO":"Prov","ECC":"Eccl","SNG":"Song","ISA":"Isa","JER":"Jer",
        "LAM":"Lam","EZK":"Ezek","DAN":"Dan","HOS":"Hos","JOL":"Joel","AMO":"Amos",
        "OBA":"Obad","JON":"Jonah","MIC":"Mic","NAM":"Nah","HAB":"Hab","ZEP":"Zeph",
        "HAG":"Hag","ZEC":"Zech","MAL":"Mal","MAT":"Matt","MRK":"Mark","LUK":"Luke",
        "JHN":"John","ACT":"Acts","ROM":"Rom","1CO":"1Cor","2CO":"2Cor","GAL":"Gal",
        "EPH":"Eph","PHP":"Phil","COL":"Col","1TH":"1Thess","2TH":"2Thess","1TI":"1Tim",
        "2TI":"2Tim","TIT":"Titus","PHM":"Phlm","HEB":"Heb","JAS":"Jas","1PE":"1Pet",
        "2PE":"2Pet","1JN":"1John","2JN":"2John","3JN":"3John","JUD":"Jude","REV":"Rev",
    }

    osis_book = BOOK_OSIS.get(book.upper(), book)
    ref = f"{osis_book}.{chapter}.{verse}"

    try:
        url = f"https://www.openbible.info/labs/cross-references/search?q={ref}&format=json"
        response = httpx.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = [
            {"reference": r.get("v2"), "votes": r.get("votes", 0)}
            for r in data
            if r.get("votes", 0) >= min_votes
        ]
        results.sort(key=lambda x: x["votes"], reverse=True)
        return results[:limit]
    except Exception as e:
        return [{"error": str(e)}]


# ── ESTUDIO PROFUNDO UNIFICADO ─────────────────────────────────────────────────

@mcp.tool()
def deep_study(
    verse_id: str,
    spanish_bible_id: str = "592420522e16049f-01",
    english_translation: str = "WEB",
    commentator: str = "matthew-henry",
    cross_ref_limit: int = 5,
) -> dict:
    """Unified deep Bible study tool. Combines verse in Spanish (API.Bible),
    verse in English (helloao.org), commentary, and cross-references in one call.

    Args:
        verse_id: Verse ID in format BOOKID.CHAPTER.VERSE (e.g. 'JHN.3.16', '2SA.11.3', 'PSA.23.1')
        spanish_bible_id: API.Bible translation ID for Spanish (default: RVR1909)
        english_translation: helloao.org translation ID for English (default: WEB)
        commentator: Commentary source (matthew-henry, adam-clarke, john-gill, jamieson-fausset-brown, keil-delitzsch, tyndale)
        cross_ref_limit: Number of cross-references to include (default 5)
    """
    result = {"verse_id": verse_id}

    # 1. Spanish verse via API.Bible
    try:
        params = {**CONTENT_PARAMS}
        data = _get(f"/bibles/{spanish_bible_id}/verses/{verse_id}", params)
        v = data.get("data", {})
        result["spanish"] = {
            "translation": "Reina-Valera 1909",
            "reference": v.get("reference", ""),
            "text": v.get("content", "").strip(),
        }
    except Exception as e:
        result["spanish"] = {"error": str(e)}

    # 2. English verse via helloao.org
    try:
        book, chapter, verse = _parse_verse_id(verse_id)
        data = _helloao_get(f"/{english_translation}/{book}/{chapter}.json")
        verses = data.get("chapter", {}).get("verses", [])
        for v in verses:
            if v.get("number") == verse:
                items = v.get("items", [])
                text = " ".join(i.get("text", "") for i in items if i.get("type") == "verse").strip()
                result["english"] = {"translation": english_translation, "text": text}
                break
    except Exception as e:
        result["english"] = {"error": str(e)}

    # 3. Commentary via helloao.org
    result["commentary"] = get_commentary(verse_id, commentator)

    # 4. Cross-references via OpenBible.info
    result["cross_references"] = get_cross_references(verse_id, limit=cross_ref_limit)

    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
