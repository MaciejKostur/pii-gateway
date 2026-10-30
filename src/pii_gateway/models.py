from dataclasses import dataclass


@dataclass(frozen=True)
class Entity:
    """Wykryty fragment z danymi osobowymi."""
    type: str
    start: int
    end: int
    score: float
