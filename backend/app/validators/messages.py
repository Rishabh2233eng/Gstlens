ISSUE_MESSAGES = {
    # gstin
    "missing": "GSTIN is missing",
    "wrong_length": "GSTIN is not 15 characters long",
    "wrong_format": "GSTIN format is invalid",
    "unknown_state_code": "GSTIN state code is not a recognized state",
    "bad_checksum": "GSTIN checksum does not match; GSTIN may be incorrect",
    # tax
    "negative_value": "A tax or amount value is negative",
    "tax_rate_over_100": "Tax rate is above 100%, which is not valid",
    "tax_amount_mismatch": "Tax amount does not match taxable value x tax rate",
    "mixed_intra_and_inter_state_tax": "Invoice charges both CGST/SGST and IGST, which should not happen",
    "cgst_sgst_not_equal": "CGST and SGST amounts should be equal but are not",
    "invoice_total_mismatch": "Invoice total does not match taxable value plus tax",
    "line_items_do_not_sum_to_invoice": "Line item taxable values do not add up to the invoice taxable value",
    # place of supply
    "igst_charged_for_same_state": "IGST charged even though supplier and buyer are in the same state",
    "cgst_sgst_charged_for_different_state": "CGST/SGST charged even though supplier and buyer are in different states",
    # dates
    "missing_date": "Invoice date is missing",
    "future_date": "Invoice date is in the future",
    "date_too_old": "Invoice date is unusually old",
    # duplicates
    "duplicate_invoice_number": "Another invoice with the same supplier GSTIN and invoice number already exists",
    "possible_duplicate_same_date_and_amount": "Another invoice from the same supplier has the same date and total amount",
}


def message_for(code: str) -> str:
    return ISSUE_MESSAGES.get(code, code.replace("_", " ").capitalize())


SEVERE_CODES = {
    "bad_checksum", "wrong_format", "wrong_length", "missing",
    "tax_amount_mismatch", "invoice_total_mismatch", "duplicate_invoice_number",
    "igst_charged_for_same_state", "cgst_sgst_charged_for_different_state",
    "line_items_do_not_sum_to_invoice",
}


def severity_for(code: str) -> str:
    return "error" if code in SEVERE_CODES else "warning"