from app.validators.tax import (
    check_invoice_totals,
    check_line_item_tax,
    check_line_items_sum_to_invoice,
    check_tax_split,
)


# --- check_line_item_tax ---

def test_line_item_tax_correct():
    assert check_line_item_tax(1000, 18, 180) == []


def test_line_item_tax_mismatch():
    assert "tax_amount_mismatch" in check_line_item_tax(1000, 18, 100)


def test_line_item_tax_within_rounding_tolerance():
    # 999.50 * 18% = 179.91, but invoice shows 180 due to rounding -> should pass
    assert check_line_item_tax(999.50, 18, 180) == []


def test_line_item_tax_missing_fields_skipped():
    assert check_line_item_tax(None, 18, 180) == []
    assert check_line_item_tax(1000, None, 180) == []
    assert check_line_item_tax(1000, 18, None) == []


def test_line_item_negative_value():
    assert "negative_value" in check_line_item_tax(-1000, 18, 180)


def test_line_item_rate_over_100():
    assert "tax_rate_over_100" in check_line_item_tax(1000, 150, 1500)


# --- check_tax_split ---

def test_tax_split_correct_intra_state():
    assert check_tax_split(cgst=90, sgst=90, igst=0) == []


def test_tax_split_correct_inter_state():
    assert check_tax_split(cgst=0, sgst=0, igst=180) == []


def test_tax_split_no_tax_at_all_is_fine():
    assert check_tax_split(cgst=0, sgst=0, igst=0) == []
    assert check_tax_split(cgst=None, sgst=None, igst=None) == []


def test_tax_split_mixed_intra_and_inter():
    assert "mixed_intra_and_inter_state_tax" in check_tax_split(cgst=90, sgst=90, igst=180)


def test_tax_split_cgst_sgst_not_equal():
    assert "cgst_sgst_not_equal" in check_tax_split(cgst=90, sgst=50, igst=0)


# --- check_invoice_totals ---

def test_invoice_totals_correct_intra_state():
    assert check_invoice_totals(1000, 90, 90, 0, 1180) == []


def test_invoice_totals_correct_inter_state():
    assert check_invoice_totals(1000, 0, 0, 180, 1180) == []


def test_invoice_totals_mismatch():
    assert "invoice_total_mismatch" in check_invoice_totals(1000, 90, 90, 0, 1500)


def test_invoice_totals_missing_fields_skipped():
    assert check_invoice_totals(None, 90, 90, 0, 1180) == []
    assert check_invoice_totals(1000, 90, 90, 0, None) == []


def test_invoice_totals_negative():
    assert "negative_value" in check_invoice_totals(-1000, 90, 90, 0, 1180)


# --- check_line_items_sum_to_invoice ---

def test_line_items_sum_matches():
    assert check_line_items_sum_to_invoice([8000, 3000], 11000) == []


def test_line_items_sum_mismatch():
    assert "line_items_do_not_sum_to_invoice" in check_line_items_sum_to_invoice([8000, 2000], 11000)


def test_line_items_sum_skipped_when_empty():
    assert check_line_items_sum_to_invoice([], 11000) == []
    assert check_line_items_sum_to_invoice([None, None], 11000) == []


def test_line_items_sum_skipped_when_invoice_total_missing():
    assert check_line_items_sum_to_invoice([8000, 3000], None) == []