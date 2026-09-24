from app.validators.gstin import gstin_state_code


def check_place_of_supply(supplier_gstin, buyer_gstin, cgst, sgst, igst) -> list[str]:
    """An invoice should charge CGST+SGST when both parties are in the same state,
    and IGST when they are in different states."""
    from app.validators.tax import _to_decimal  # local import avoids a circular import

    supplier_state = gstin_state_code(supplier_gstin)
    buyer_state = gstin_state_code(buyer_gstin)

    if supplier_state is None or buyer_state is None:
        return []  # can't tell; a bad GSTIN is already flagged by the GSTIN validator

    c = _to_decimal(cgst) or 0
    s = _to_decimal(sgst) or 0
    i = _to_decimal(igst) or 0
    has_intra = c > 0 or s > 0
    has_inter = i > 0

    if not has_intra and not has_inter:
        return []  # no tax charged at all; nothing to check here

    same_state = supplier_state == buyer_state
    problems = []

    if same_state and has_inter:
        problems.append("igst_charged_for_same_state")
    if not same_state and has_intra:
        problems.append("cgst_sgst_charged_for_different_state")

    return problems