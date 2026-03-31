"""
turkish.py
==========
Turkish character utilities.

Python's built-in str.upper() handles dotted-i (İ) incorrectly on some
locales. This module provides a locale-independent implementation.
"""


_UPPER_MAP: dict[str, str] = {
    "i": "İ",
    "ı": "I",
    "ç": "Ç",
    "ğ": "Ğ",
    "ö": "Ö",
    "ş": "Ş",
    "ü": "Ü",
}


def to_turkish_upper(text: str) -> str:
    """Return *text* converted to uppercase with correct Turkish rules.

    Example
    -------
    >>> to_turkish_upper("istanbul")
    'İSTANBUL'
    >>> to_turkish_upper("ışık")
    'IŞIK'
    """
    result: list[str] = []
    for ch in text:
        lower = ch.lower()
        if lower in _UPPER_MAP:
            result.append(_UPPER_MAP[lower])
        else:
            result.append(ch.upper())
    return "".join(result)
