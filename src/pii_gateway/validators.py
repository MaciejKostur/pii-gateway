"""Czyste funkcje walidujace sumy kontrolne. Bez zaleznosci zewnetrznych."""
import re


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def is_valid_pesel(value: str) -> bool:
    d = _digits(value)
    if len(d) != 11:
        return False
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    s = sum(int(x) * w for x, w in zip(d[:10], weights))
    return (10 - s % 10) % 10 == int(d[10])


def is_valid_nip(value: str) -> bool:
    d = _digits(value)
    if len(d) != 10:
        return False
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    check = sum(int(x) * w for x, w in zip(d[:9], weights)) % 11
    return check != 10 and check == int(d[9])


def is_valid_regon(value: str) -> bool:
    d = _digits(value)
    if len(d) == 9:
        weights = [8, 9, 2, 3, 4, 5, 6, 7]
        check = sum(int(x) * w for x, w in zip(d[:8], weights)) % 11 % 10
        return check == int(d[8])
    if len(d) == 14:
        weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
        check = sum(int(x) * w for x, w in zip(d[:13], weights)) % 11 % 10
        return is_valid_regon(d[:9]) and check == int(d[13])
    return False


def is_valid_iban_pl(value: str) -> bool:
    iban = re.sub(r"\s", "", value).upper()
    if not iban.startswith("PL"):
        iban = "PL" + iban
    if len(iban) != 28 or not iban[2:].isdigit():
        return False
    rearranged = iban[4:] + iban[:4]
    numeric = "".join(str(int(c, 36)) for c in rearranged)
    return int(numeric) % 97 == 1


def is_valid_luhn(value: str) -> bool:
    d = _digits(value)
    if not 13 <= len(d) <= 19:
        return False
    total = 0
    for i, ch in enumerate(reversed(d)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def is_valid_dowod(value: str) -> bool:
    """Numer dowodu osobistego: 3 litery + 6 cyfr."""
    v = re.sub(r"\s", "", value).upper()
    if not re.fullmatch(r"[A-Z]{3}\d{6}", v):
        return False
    weights = [7, 3, 1, 9, 7, 3, 1, 7, 3]
    total = sum(int(c, 36) * w for c, w in zip(v, weights))
    return total % 10 == 0
