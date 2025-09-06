from .types import LanguageItem

API_URL = "https://store.steampowered.com/events/ajaxgetpartnereventspageable/"

LANGUAGE_MAP: list[LanguageItem] = [
    {"lang": "english", "code": "en"},
    {"lang": "german", "code": "de"},
    {"lang": "french", "code": "fr"},
]
