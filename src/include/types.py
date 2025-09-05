from enum import Enum
from typing import TypedDict


class EventType(Enum):
    UPDATE = 12
    NEWS = 13


class FeedItem(TypedDict):
    guid: str
    event_type: int
    updatetime: int
    headline: str
    language: int
    body: str
    url: str


class LanguageItem(TypedDict):
    lang: str
    code: str
