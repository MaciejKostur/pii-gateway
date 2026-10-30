import pytest

from pii_gateway.anonymizer import Mode, PIIBlockedError, anonymize
from pii_gateway.models import Entity
from pii_gateway.vault import Vault

PESEL = "44051401359"
MAIL = "a@b.pl"
TEXT = f"PESEL {PESEL}, mail {MAIL}, znowu {PESEL}."


def _span(value, nth=0):
    start = -1
    for _ in range(nth + 1):
        start = TEXT.index(value, start + 1)
    return start, start + len(value)


ENTS = [
    Entity("PL_PESEL", *_span(PESEL, 0), 1.0),
    Entity("EMAIL_ADDRESS", *_span(MAIL), 0.9),
    Entity("PL_PESEL", *_span(PESEL, 1), 1.0),
]


def test_pseudonymize_same_value_same_token():
    out = anonymize(TEXT, ENTS, Mode.PSEUDONYMIZE, Vault(), "s1")
    assert out == "PESEL <PL_PESEL_1>, mail <EMAIL_ADDRESS_1>, znowu <PL_PESEL_1>."


def test_roundtrip():
    vault = Vault()
    out = anonymize(TEXT, ENTS, Mode.PSEUDONYMIZE, vault, "s1")
    assert vault.restore("s1", out) == TEXT


def test_sessions_are_isolated():
    vault = Vault()
    anonymize(TEXT, ENTS, Mode.PSEUDONYMIZE, vault, "s1")
    assert vault.restore("s2", "<PL_PESEL_1>") == "<PL_PESEL_1>"


def test_mask():
    out = anonymize(TEXT, ENTS, Mode.MASK)
    assert "44051401359" not in out and "***********" in out


def test_block():
    with pytest.raises(PIIBlockedError):
        anonymize(TEXT, ENTS, Mode.BLOCK)


def test_overlap_prefers_higher_score():
    text = "123456785"
    ents = [Entity("PHONE_NUMBER", 0, 9, 0.5), Entity("PL_REGON", 0, 9, 1.0)]
    assert anonymize(text, ents, Mode.PSEUDONYMIZE, Vault()) == "<PL_REGON_1>"
