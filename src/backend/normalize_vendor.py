import re

from src.backend.procurement_models import (
    VendorQuote,
    QuoteItem,
    NormalizedVendorQuote,
)
from src.backend.rfq import RFQ_ITEMS
from src.backend.uom import normalize_uom


def extract_pack_size(uom: str):
    """
    Extract explicit pack size from UOM text.

    Examples:
        '100 pcs/box'          -> 100
        '100 pieces per box'   -> 100
        'box of 100'           -> 100
        'box'                  -> None
        'pcs'                  -> None
    """

    if not uom:
        return None

    value = str(uom).strip().lower()

    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:pcs?|pieces?)\s*(?:/|per|in)\s*(?:box|boxes)",
        r"(?:box|boxes)\s*(?:of|x)\s*(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, value)

        if match:
            return float(match.group(1))

    return None


def normalize_vendor(vendor_info, items):

    # -----------------------------------------
    # 1. Normalize vendor metadata
    # -----------------------------------------

    vendor_data = {}

    for row in vendor_info:

        if not row:
            continue

        for key, value in row.items():

            key = str(key).strip()
            value = str(value).strip()

            if key and value:
                vendor_data[key] = value

    # -----------------------------------------
    # 2. Extract vendor fields
    # -----------------------------------------

    vendor_name = (
        vendor_data.get("Vendor")
        or vendor_data.get("Vendor Name")
        or vendor_data.get("Supplier")
        or ""
    )

    quote_ref = (
        vendor_data.get("Quote Ref")
        or vendor_data.get("Quote Reference")
        or vendor_data.get("Quotation No")
        or ""
    )

    quote_date = (
        vendor_data.get("Quote Date")
        or vendor_data.get("Quotation Date")
        or ""
    )

    currency = (
        vendor_data.get("Currency")
        or vendor_data.get("Quote Currency")
        or ""
    ).strip()

    validity = (
        vendor_data.get("Validity")
        or vendor_data.get("Quote Validity")
        or ""
    )

    payment_terms = (
        vendor_data.get("Payment Terms")
        or vendor_data.get("Payment")
        or ""
    )

    delivery_terms = (
        vendor_data.get("Delivery Terms")
        or vendor_data.get("Delivery")
        or ""
    )

    gst = (
        vendor_data.get("GST")
        or vendor_data.get("GST / Taxes")
        or vendor_data.get("Taxes")
        or ""
    )

    vendor_quote = VendorQuote(
        vendor_name=vendor_name,
        quote_ref=quote_ref,
        quote_date=quote_date,
        currency=currency,
        validity=validity,
        payment_terms=payment_terms,
        delivery_terms=delivery_terms,
        gst=gst,
    )

    # -----------------------------------------
    # 3. Normalize quote items
    # -----------------------------------------

    normalized_items = []

    for item in items:

        item_id = (
            item.get("Item ID")
            or item.get("Item")
            or item.get("Item Code")
            or item.get("SKU")
            or ""
        )

        description = (
            item.get("Description")
            or item.get("Item Description")
            or ""
        )

        qty = (
            item.get("RFQ Qty")
            or item.get("Qty")
            or item.get("Quantity")
            or 0
        )

        quoted_uom = (
            item.get("UOM")
            or item.get("Unit")
            or item.get("Unit of Measure")
            or ""
        )

        price = (
            item.get("Unit Price")
            or item.get("Price")
            or item.get("Rate")
            or 0
        )

        lead_time = (
            item.get("Lead Time")
            or item.get("Delivery")
            or ""
        )

        # -----------------------------------------
        # Find corresponding RFQ item
        # -----------------------------------------

        rfq_item = next(
            (
                rfq
                for rfq in RFQ_ITEMS
                if rfq.item_id == item_id
            ),
            None,
        )

        if not rfq_item:
            continue

        # -----------------------------------------
        # Normalize price
        # -----------------------------------------

        if isinstance(price, str):

            price = (
                price.replace("₹", "")
                .replace("$", "")
                .replace(",", "")
                .strip()
            )

        try:
            price = float(price)

        except (ValueError, TypeError):

            price = None

        # -----------------------------------------
        # Normalize quantity
        # -----------------------------------------

        try:
            qty = float(qty)

        except (ValueError, TypeError):

            qty = 0

        # -----------------------------------------
        # Normalize lead time
        # -----------------------------------------

        if isinstance(lead_time, str):

            lead_time = (
                lead_time.lower()
                .replace("days", "")
                .replace("day", "")
                .strip()
            )

        try:
            lead_time = int(lead_time)

        except (ValueError, TypeError):

            lead_time = None

        # -----------------------------------------
        # Normalize UOM
        # -----------------------------------------

        rfq_uom = normalize_uom(rfq_item.uom)

        # Keep original UOM text before normalization
        raw_quoted_uom = quoted_uom

        # Extract explicit pack size
        pack_size = extract_pack_size(raw_quoted_uom)

        # Normalize UOM name
        quoted_uom = normalize_uom(quoted_uom)

        # -----------------------------------------
        # Create normalized item
        # -----------------------------------------

        normalized_items.append(
            QuoteItem(
                item_id=item_id,
                description=description,
                rfq_qty=qty,
                rfq_uom=rfq_uom,
                quoted_uom=quoted_uom,
                unit_price=price,

                # IMPORTANT:
                # Use vendor-level currency
                currency=currency,

                lead_time_days=lead_time,

                uom_conversion_required=(
                    rfq_uom != quoted_uom
                ),

                currency_normalization_required=(
                    currency.upper() != "INR"
                ),

                pack_size=pack_size,
            )
        )

    # -----------------------------------------
    # 4. Return normalized vendor quote
    # -----------------------------------------

    return NormalizedVendorQuote(
        vendor=vendor_quote,
        items=normalized_items,
        validation_passed=False,
        validation_issues=[],
    )