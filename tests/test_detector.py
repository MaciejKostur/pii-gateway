"""Wymagaja zainstalowanego presidio-analyzer i modelu pl_core_news_lg."""
import pytest

pytest.importorskip("presidio_analyzer")
from pii_gateway.detector import Detector  # noqa: E402

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def detector():
    return Detector()


def types(detector, text):
    return {e.type for e in detector.detect(text)}


def test_valid_pesel_detected(detector):
    assert "PL_PESEL" in types(detector, "Moj PESEL to 44051401359.")


def test_invalid_pesel_ignored(detector):
    assert "PL_PESEL" not in types(detector, "Numer zamowienia 44051401358.")


def test_email_and_phone(detector):
    t = types(detector, "Pisz na jan.kowalski@example.com lub dzwon +48 600 700 800.")
    assert {"EMAIL_ADDRESS", "PHONE_NUMBER"} <= t


def test_iban(detector):
    assert "IBAN_CODE" in types(detector, "Konto: PL61 1090 1014 0000 0712 1981 2874")


def test_person_ner(detector):
    assert "PERSON" in types(detector, "Spotkalem sie z Janem Kowalskim w Lublinie.")
