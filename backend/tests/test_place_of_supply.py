from app.validators.place_of_supply import check_place_of_supply

SAME_STATE_A = "27ABCDE1234F1Z5"  # state 27
SAME_STATE_B = "27PQRSX5678L1Z2"  # state 27
OTHER_STATE = "07LMNOP4321Q1Z9"   # state 07


def test_correct_intra_state_cgst_sgst():
    assert check_place_of_supply(SAME_STATE_A, SAME_STATE_B, cgst=90, sgst=90, igst=0) == []


def test_correct_inter_state_igst():
    assert check_place_of_supply(SAME_STATE_A, OTHER_STATE, cgst=0, sgst=0, igst=180) == []


def test_igst_charged_for_same_state_is_wrong():
    problems = check_place_of_supply(SAME_STATE_A, SAME_STATE_B, cgst=0, sgst=0, igst=180)
    assert "igst_charged_for_same_state" in problems


def test_cgst_sgst_charged_for_different_state_is_wrong():
    problems = check_place_of_supply(SAME_STATE_A, OTHER_STATE, cgst=90, sgst=90, igst=0)
    assert "cgst_sgst_charged_for_different_state" in problems


def test_no_tax_charged_is_skipped():
    assert check_place_of_supply(SAME_STATE_A, OTHER_STATE, cgst=0, sgst=0, igst=0) == []


def test_missing_gstin_is_skipped():
    assert check_place_of_supply(None, SAME_STATE_B, cgst=90, sgst=90, igst=0) == []
    assert check_place_of_supply(SAME_STATE_A, None, cgst=90, sgst=90, igst=0) == []


def test_short_or_invalid_gstin_is_skipped():
    assert check_place_of_supply("123", SAME_STATE_B, cgst=90, sgst=90, igst=0) == []