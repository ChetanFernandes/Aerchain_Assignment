from src.backend.procurement_models import NormalizedVendorQuote


def build_comparison(vendor_quotes: list[NormalizedVendorQuote]):
    rows = []

    for vendor_quote in vendor_quotes:
        for item in vendor_quote.items:
            rows.append(
                {
                    "item_id": item.item_id,
                    "description": item.description,
                    "vendor": vendor_quote.vendor.vendor_name,
                    "price": item.unit_price,
                    "currency": item.currency,
                    "uom": item.quoted_uom,
                    "lead_time_days": item.lead_time_days,
                    "validation_passed": vendor_quote.validation_passed,
                }
            )

    return rows