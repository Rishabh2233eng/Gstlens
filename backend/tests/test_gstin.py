from app.validators.gstin import (
    gstin_state_code,
    is_valid_gstin,
    validate_gstin,
)


def real_valid_gstin() -> str:
    # 27AAPFU0939F1ZV is a well-known, publicly documented example GSTIN
    # used in official GST education material.
    return "27AAPFU0939F1ZV"


def test_valid_gstin_passes():
    assert validate_gstin(real_valid_gstin()) == []
    assert is_valid_gstin(real_valid_gstin()) is True


def test_missing_gstin():
    assert validate_gstin(None) == ["missing"]
    assert validate_gstin("") == ["missing"]


def test_wrong_length():
    assert "wrong_length" in validate_gstin("27AAPFU0939F1Z")
    assert "wrong_length" in validate_gstin("27AAPFU0939F1ZVX")


def test_wrong_format_lowercase_letters_in_pan_slot():
    bad = "27aapfu0939f1zv".upper()  # uppercased first, still wrong pattern below
    broken = "27AAPF#0939F1ZV"  # symbol where a letter/digit should be
    assert "wrong_format" in validate_gstin(broken)


def test_unknown_state_code():
    bad = "99AAPFU0939F1ZV"  # 99 is not an allotted state code
    assert "unknown_state_code" in validate_gstin(bad)


def test_bad_checksum():
    valid = real_valid_gstin()
    corrupted = valid[:14] + ("A" if valid[14] != "A" else "B")
    problems = validate_gstin(corrupted)
    assert "bad_checksum" in problems


def test_case_and_whitespace_are_normalized():
    valid = real_valid_gstin()
    messy = f"  {valid.lower()}  "
    assert validate_gstin(messy) == []


def test_state_code_extraction():
    assert gstin_state_code("27AAPFU0939F1ZV") == "27"
    assert gstin_state_code("9") is None
    assert gstin_state_code(None) is None


def test_entity_code_z_position_enforced():
    # 14th character (index 13, 0-based) must always be 'Z'
    valid = real_valid_gstin()
    bad = valid[:13] + "X" + valid[14:]
    assert "wrong_format" in validate_gstin(bad)