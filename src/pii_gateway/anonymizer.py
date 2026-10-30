from enum import Enum

from .models import Entity
from .vault import Vault


class Mode(str, Enum):
    BLOCK = "block"
    MASK = "mask"
    PSEUDONYMIZE = "pseudonymize"


class PIIBlockedError(Exception):
    def __init__(self, types: list[str]):
        self.types = types
        super().__init__(f"Wykryto dane osobowe: {', '.join(types)}")


def resolve_overlaps(entities: list[Entity]) -> list[Entity]:
    """Przy nakladaniu sie wygrywa wyzszy score, potem dluzszy fragment."""
    ranked = sorted(entities, key=lambda e: (-e.score, -(e.end - e.start), e.start))
    chosen: list[Entity] = []
    for e in ranked:
        if all(e.end <= c.start or e.start >= c.end for c in chosen):
            chosen.append(e)
    return sorted(chosen, key=lambda e: e.start)


def anonymize(text: str, entities: list[Entity], mode: Mode = Mode.PSEUDONYMIZE,
              vault: Vault | None = None, session_id: str = "default") -> str:
    entities = resolve_overlaps(entities)
    if mode == Mode.BLOCK:
        if entities:
            raise PIIBlockedError(sorted({e.type for e in entities}))
        return text
    if mode == Mode.PSEUDONYMIZE and vault is None:
        raise ValueError("Tryb pseudonymize wymaga vaulta")

    out, last = [], 0
    for e in entities:
        out.append(text[last:e.start])
        original = text[e.start:e.end]
        if mode == Mode.MASK:
            out.append("*" * len(original))
        else:
            out.append(vault.get_token(session_id, e.type, original))
        last = e.end
    out.append(text[last:])
    return "".join(out)
