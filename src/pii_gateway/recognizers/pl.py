"""Polskie recognizery oparte o regex + walidacje sum kontrolnych."""
from typing import Callable, Optional

from presidio_analyzer import Pattern, PatternRecognizer

from .. import validators as v

LANG = "pl"


class ValidatedRecognizer(PatternRecognizer):
    """PatternRecognizer, ktory odrzuca dopasowania z bledna suma kontrolna."""

    def __init__(self, entity: str, regex: str, validator: Optional[Callable[[str], bool]],
                 score: float, context: Optional[list[str]] = None):
        super().__init__(
            supported_entity=entity,
            patterns=[Pattern(name=f"{entity}_pattern", regex=regex, score=score)],
            context=context,
            supported_language=LANG,
        )
        self._validator = validator

    def validate_result(self, pattern_text: str):
        if self._validator is None:
            return None  # brak walidacji -> zostaje bazowy score
        # True -> score 1.0, False -> wynik odrzucony
        return self._validator(pattern_text)


def build_recognizers() -> list[PatternRecognizer]:
    return [
        ValidatedRecognizer(
            "PL_PESEL", r"(?<!\d)\d{11}(?!\d)", v.is_valid_pesel, 0.4,
            context=["pesel"],
        ),
        ValidatedRecognizer(
            "PL_NIP",
            r"(?<!\d)(?:\d{10}|\d{3}-\d{3}-\d{2}-\d{2}|\d{3}-\d{2}-\d{2}-\d{3})(?!\d)",
            v.is_valid_nip, 0.4, context=["nip"],
        ),
        ValidatedRecognizer(
            "PL_REGON", r"(?<!\d)(?:\d{14}|\d{9})(?!\d)", v.is_valid_regon, 0.3,
            context=["regon"],
        ),
        ValidatedRecognizer(
            "IBAN_CODE", r"(?<![\dA-Za-z])(?:PL)?\s?\d{2}(?:\s?\d{4}){6}(?!\d)",
            v.is_valid_iban_pl, 0.4, context=["iban", "konto", "rachunek"],
        ),
        ValidatedRecognizer(
            "CREDIT_CARD", r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)", v.is_valid_luhn, 0.3,
            context=["karta", "karty", "card"],
        ),
        ValidatedRecognizer(
            "PL_ID_CARD", r"(?<![A-Za-z])[A-Za-z]{3}\s?\d{6}(?!\d)", v.is_valid_dowod, 0.4,
            context=["dowod", "dowodu", "dowodzie"],
        ),
        ValidatedRecognizer(
            "PHONE_NUMBER",
            r"(?<!\d)(?:\+48[ -]?|0048[ -]?)?\d{3}[ -]?\d{3}[ -]?\d{3}(?!\d)",
            None, 0.5, context=["tel", "telefon", "numer", "komorka"],
        ),
        ValidatedRecognizer(
            "EMAIL_ADDRESS", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            None, 0.9,
        ),
    ]
