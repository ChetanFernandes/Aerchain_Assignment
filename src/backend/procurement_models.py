from dataclasses import dataclass
from typing import Optional


@dataclass
class VendorQuote:
    vendor_name: str
    quote_ref: str
    quote_date: str
    currency: str
    validity: str
    payment_terms: str
    delivery_terms: str
    gst: str


@dataclass
class QuoteItem:
    item_id: str
    description: str
    rfq_qty: float
    rfq_uom: str
    quoted_uom: str
    unit_price: Optional[float]
    currency: str
    lead_time_days: Optional[int]
    uom_conversion_required: bool = False
    currency_normalization_required: bool = False
    pack_size: Optional[float] = None

@dataclass
class NormalizedVendorQuote:
    vendor: VendorQuote
    items: list[QuoteItem]
    validation_passed: bool
    validation_issues: list[str]