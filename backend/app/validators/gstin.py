import re

STATE_CODES = {
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38",
    "97",  # other territory
}

_GSTIN_PATTERN = re.compile(
    r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
)

_CHECKSUM_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _checksum_char(gstin_without_checksum: str) -> str:
    """Computes the official GSTIN checksum character (ISO 7064 MOD 36)."""
    factor = 2
    total = 0
    for ch in reversed(gstin_without_checksum):
        digit = _CHECKSUM_CHARS.index(ch)
        product = factor * digit
        product = (product // 36) + (product % 36)
        total += product
        factor = 1 if factor == 2 else 2
    remainder = total % 36
    check_digit_value = (36 - remainder) % 36
    return _CHECKSUM_CHARS[check_digit_value]


def validate_gstin(gstin: str | None) -> list[str]:
    """Returns a list of problems found. An empty list means the GSTIN is valid."""
    if not gstin:
        return ["missing"]

    gstin = gstin.strip().upper()
    problems = []

    if len(gstin) != 15:
        problems.append("wrong_length")
        return problems  # further checks need exactly 15 characters

    if not _GSTIN_PATTERN.match(gstin):
        problems.append("wrong_format")

    state_code = gstin[:2]
    if state_code not in STATE_CODES:
        problems.append("unknown_state_code")

    if not problems:
        expected = _checksum_char(gstin[:14])
        if gstin[14] != expected:
            problems.append("bad_checksum")

    return problems


def is_valid_gstin(gstin: str | None) -> bool:
    return validate_gstin(gstin) == []


def gstin_state_code(gstin: str | None) -> str | None:
    if gstin and len(gstin) >= 2 and gstin[:2].isdigit():
        return gstin[:2]
    return None