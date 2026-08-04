from dataclasses import dataclass

@dataclass(slots=True)
class NewsMessage:
    time: int
    category: str
    headline: str
    summary: str