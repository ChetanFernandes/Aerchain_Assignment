from src.backend.procurement_models import VendorQuote, QuoteItem
from dataclasses import dataclass


@dataclass
class ValidationResult:
    passed: bool
    issues: list[str]
    missing_items: list[str]
    unexpected_items: list[str]

def validate_vendor_quote(
    vendor: VendorQuote,
    items: list[QuoteItem],
    expected_item_ids: list[str],
):
    issues = []

    if not vendor.vendor_name:
        issues.append("Vendor name is missing.")

    if not vendor.currency:
        issues.append("Currency is missing.")

    quoted_item_ids = {
        item.item_id
        for item in items
        if item.item_id
    }

    expected_ids = set(expected_item_ids)

    missing_items = sorted(expected_ids - quoted_item_ids)

    if missing_items:
        issues.append(
            f"Missing quoted items: {', '.join(sorted(missing_items))}"
        )

    unexpected_items =  sorted(quoted_item_ids - expected_ids)

    if unexpected_items:
        issues.append(
            f"Unexpected item IDs: {', '.join(sorted(unexpected_items))}"
        )

    for item in items:

        if item.rfq_qty <= 0:
            issues.append(
                f"{item.item_id}: Invalid RFQ quantity."
            )

        if item.unit_price is None:
            issues.append(
                f"{item.item_id}: Unit price is missing."
            )

        if item.unit_price is not None and item.unit_price < 0:
            issues.append(
                f"{item.item_id}: Unit price cannot be negative."
            )

        if not item.quoted_uom:
            issues.append(f"{item.item_id}: Quoted UOM is missing.")

        if not item.rfq_uom:
            issues.append(f"{item.item_id}: RFQ UOM is missing.")

        if item.rfq_uom and item.quoted_uom:
            if item.rfq_uom != item.quoted_uom:
                issues.append(
                    f"{item.item_id}: UOM mismatch "
                    f"(RFQ requires {item.rfq_uom}, "
                    f"vendor quoted {item.quoted_uom})."
                )

        if item.uom_conversion_required:

            if item.pack_size:
                issues.append(
                    f"{item.item_id}: UOM conversion required "
                    f"({item.rfq_uom} -> {item.quoted_uom}); "
                    f"vendor states {item.pack_size:g} "
                    f"{item.rfq_uom} per {item.quoted_uom}. "
                    f"Buyer review required."
                )

            else:
                issues.append(
                    f"{item.item_id}: UOM conversion required "
                    f"({item.rfq_uom} -> {item.quoted_uom}) "
                    f"and pack size is not specified. "
                    f"Buyer review required."
                )


    return ValidationResult(
    passed=len(issues) == 0,
    issues=issues,
    missing_items=missing_items,
    unexpected_items=unexpected_items,
)