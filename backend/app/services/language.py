import logging
import re
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
}

# ISO 639-2 / BCP-47 / Name mappings to ISO 639-1
_LANGUAGE_ALIASES: Dict[str, str] = {
    "english": "en",
    "eng": "en",
    "hindi": "hi",
    "hin": "hi",
    "bengali": "bn",
    "ben": "bn",
    "bangla": "bn",
    "marathi": "mr",
    "mar": "mr",
    "tamil": "ta",
    "tam": "ta",
    "telugu": "te",
    "tel": "te",
    "gujarati": "gu",
    "guj": "gu",
    "kannada": "kn",
    "kan": "kn",
    "malayalam": "ml",
    "mal": "ml",
    "punjabi": "pa",
    "pan": "pa",
}

# Unicode block ranges for Indic scripts
_SCRIPT_RANGES = [
    (0x0900, 0x097F, "devanagari"),   # Hindi, Marathi, Sanskrit, Nepali
    (0x0980, 0x09FF, "bn"),           # Bengali, Assamese
    (0x0A00, 0x0A7F, "pa"),           # Punjabi (Gurmukhi)
    (0x0A80, 0x0AFF, "gu"),           # Gujarati
    (0x0B80, 0x0BFF, "ta"),           # Tamil
    (0x0C00, 0x0C7F, "te"),           # Telugu
    (0x0C80, 0x0CFF, "kn"),           # Kannada
    (0x0D00, 0x0D7F, "ml"),           # Malayalam
]

# Common Marathi marker words to differentiate Devanagari Marathi from Hindi
_MARATHI_MARKERS = {
    "आहे", "आहेत", "माहिती", "हवी", "होते", "आणि", "कसा", "कशी", "करावे", "मिळेल", "योजनेची", "मला"
}


def normalize_language_code(code: Optional[str], default: str = "en") -> str:
    """Normalize input language string to supported ISO 639-1 code.

    Handles ISO 639-1, ISO 639-2, BCP-47 locale tags (e.g. 'hi-IN', 'en_US'),
    and full language names (e.g. 'Hindi', 'English').
    """
    if not code or not str(code).strip():
        return default

    clean = str(code).strip().lower()

    # If it's already a supported 2-letter ISO code
    if clean in SUPPORTED_LANGUAGES:
        return clean

    # Check locale with hyphen or underscore (e.g. "hi-IN", "en_US")
    base = re.split(r"[-_]", clean)[0]
    if base in SUPPORTED_LANGUAGES:
        return base

    # Check language aliases
    if clean in _LANGUAGE_ALIASES:
        return _LANGUAGE_ALIASES[clean]
    if base in _LANGUAGE_ALIASES:
        return _LANGUAGE_ALIASES[base]

    return default


class LanguageService:
    """Service for language detection across Indian languages and English."""

    def __init__(self, default_language: str = "en"):
        self.default_language = default_language

    async def detect_language(self, text: str) -> str:
        """Detect the ISO 639-1 language code of the input text.

        Uses script detection as high-confidence fast-path, with online fallback
        when ambiguous.
        """
        if not text or not text.strip():
            return self.default_language

        clean_text = text.strip()

        # Count character frequencies across Indic unicode script ranges
        script_counts: Dict[str, int] = {}
        latin_count = 0

        for ch in clean_text:
            code = ord(ch)
            if ("a" <= ch <= "z") or ("A" <= ch <= "Z"):
                latin_count += 1
                continue

            for start, end, script in _SCRIPT_RANGES:
                if start <= code <= end:
                    script_counts[script] = script_counts.get(script, 0) + 1
                    break

        # Check if Indic script dominates
        if script_counts:
            top_script = max(script_counts, key=script_counts.get)
            if top_script == "devanagari":
                # Disambiguate Marathi vs Hindi
                if any(marker in clean_text for marker in _MARATHI_MARKERS):
                    return "mr"
                return "hi"
            return top_script

        # If predominantly Latin characters, default to English
        if latin_count > 0:
            return "en"

        # Online detection fallback for queries with symbols / digits / ambiguous scripts
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={
                        "client": "gtx",
                        "sl": "auto",
                        "tl": "en",
                        "dt": "t",
                        "q": clean_text,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and len(data) > 2 and data[2]:
                        detected = str(data[2]).lower()
                        return normalize_language_code(detected, default=self.default_language)
        except Exception as err:
            logger.warning(f"Online language detection fallback failed: {err}")

        return self.default_language
