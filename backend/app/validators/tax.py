from decimal import Decimal, InvalidOperation

TOLERANCE = Decimal("1.00")  # allow up to Re 1 rounding difference


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _close(a: Decimal, b: Decimal, tolerance: Decimal = TOLERANCE) -> bool:
    return abs(a - b) <= tolerance


def check_line_item_tax(taxable_value, tax_rate, tax_amount) -> list[str]:
    """Checks that taxable_value * tax_rate / 100 == tax_amount for one line."""
    tv = _to_decimal(taxable_value)
    rate = _to_decimal(tax_rate)
    amount = _to_decimal(tax_amount)

    problems = []
    if tv is None or rate is None or amount is None:
        return problems  # can't check what isn't there; missing-field checks live elsewhere

    if tv < 0 or rate < 0 or amount < 0:
        problems.append("negative_value")
        return problems

    if rate > 100:
        problems.append("tax_rate_over_100")

    expected = (tv * rate / Decimal("100")).quantize(Decimal("0.01"))
    if not _close(expected, amount):
        problems.append("tax_amount_mismatch")

    return problems


def check_tax_split(cgst, sgst, igst) -> list[str]:
    """An invoice should use either (CGST + SGST) or IGST, never both, never neither
    when any tax is charged at all."""
    c = _to_decimal(cgst) or Decimal("0")
    s = _to_decimal(sgst) or Decimal("0")
    i = _to_decimal(igst) or Decimal("0")

    problems = []
    has_intra = c > 0 or s > 0
    has_inter = i > 0

    if has_intra and has_inter:
        problems.append("mixed_intra_and_inter_state_tax")

    if has_intra and not _close(c, s):
        problems.append("cgst_sgst_not_equal")

    return problems


def check_invoice_totals(taxable_value, cgst, sgst, igst, total_amount) -> list[str]:
    """Checks that taxable_value + total tax == total_amount."""
    tv = _to_decimal(taxable_value)
    total = _to_decimal(total_amount)
    if tv is None or total is None:
        return []

    c = _to_decimal(cgst) or Decimal("0")
    s = _to_decimal(sgst) or Decimal("0")
    i = _to_decimal(igst) or Decimal("0")

    problems = []
    if total < 0 or tv < 0:
        problems.append("negative_value")
        return problems

    expected_total = (tv + c + s + i).quantize(Decimal("0.01"))
    if not _close(expected_total, total):
        problems.append("invoice_total_mismatch")

    return problems


def check_line_items_sum_to_invoice(line_taxable_values, invoice_taxable_value) -> list[str]:
    """Checks that the sum of each line's taxable value matches the invoice-level
    taxable value. Skipped if there are no usable line values."""
    values = [_to_decimal(v) for v in line_taxable_values]
    values = [v for v in values if v is not None]
    invoice_tv = _to_decimal(invoice_taxable_value)

    if not values or invoice_tv is None:
        return []

    line_sum = sum(values).quantize(Decimal("0.01"))
    if not _close(line_sum, invoice_tv):
        return ["line_items_do_not_sum_to_invoice"]
    return []