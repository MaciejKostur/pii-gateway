import pytest

from pii_gateway import validators as v


@pytest.mark.parametrize("value,expected", [
    ("44051401359", True),
    ("44051401358", False),
    ("1234567890", False),
    ("abc", False),
])
def test_pesel(value, expected):
    assert v.is_valid_pesel(value) is expected


@pytest.mark.parametrize("value,expected", [
    ("1234563218", True),
    ("123-456-32-18", True),
    ("1234563219", False),
])
def test_nip(value, expected):
    assert v.is_valid_nip(value) is expected


@pytest.mark.parametrize("value,expected", [
    ("123456785", True),
    ("123456786", False),
    ("12345678512347", True),
    ("12345678512348", False),
])
def test_regon(value, expected):
    assert v.is_valid_regon(value) is expected


@pytest.mark.parametrize("value,expected", [
    ("PL61109010140000071219812874", True),
    ("61 1090 1014 0000 0712 1981 2874", True),
    ("PL61109010140000071219812875", False),
])
def test_iban(value, expected):
    assert v.is_valid_iban_pl(value) is expected


@pytest.mark.parametrize("value,expected", [
    ("4111111111111111", True),
    ("4111 1111 1111 1112", False),
])
def test_luhn(value, expected):
    assert v.is_valid_luhn(value) is expected


@pytest.mark.parametrize("value,expected", [
    ("ABA300000", True),
    ("ABA400000", False),
    ("AB1234567", False),
])
def test_dowod(value, expected):
    assert v.is_valid_dowod(value) is expected
