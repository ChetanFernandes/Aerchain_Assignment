from langchain_core.tools import tool

from src.backend.database import (
    get_vendors,
    get_vendor_items,
    get_questionnaire,
)
from src.backend.rfq import RFQ_ITEM_IDS

@tool
def list_vendors():
    """
    Get all vendor quotes currently stored in the procurement database.

    Use this when the buyer wants to know which vendors have submitted
    quotations.
    """

    return get_vendors()


@tool
def get_items_for_vendor(vendor_id: int):
    """
    Get all quoted items for a specific vendor.

    Args:
        vendor_id: The database ID of the vendor.
    """

    return get_vendor_items(vendor_id)


@tool
def get_questionnaire_for_vendor(vendor_id: int):
    """
    Get questionnaire responses for a specific vendor.

    Args:
        vendor_id: The database ID of the vendor.
    """

    return get_questionnaire(vendor_id)

@tool
def get_uom_mismatches(vendor_id: int):
    """
    Get quote items where the vendor's quoted unit of measure
    differs from the RFQ unit of measure.

    Args:
        vendor_id: The database ID of the vendor.
    """

    items = get_vendor_items(vendor_id)

    return [
        {
            "item_id": item["item_id"],
            "description": item["description"],
            "rfq_uom": item["rfq_uom"],
            "quoted_uom": item["quoted_uom"],
            "uom_conversion_required": item["uom_conversion_required"],
        }
        for item in items
        if item["uom_conversion_required"]
    ]

@tool
def get_missing_items(vendor_id: int):
    """
    Return the RFQ item IDs that are missing from a vendor's quotation.

    This compares the vendor's stored quote against the authoritative
    RFQ item list.
    """
    items = get_vendor_items(vendor_id)

    quoted_ids = {
        item["item_id"]
        for item in items
    }

    return [
        item_id
        for item_id in RFQ_ITEM_IDS
        if item_id not in quoted_ids
    ]

@tool
def get_uom_mismatches(vendor_id: int):
    """
    Return quote items where the vendor's UOM differs from the RFQ UOM.
    """
    items = get_vendor_items(vendor_id)

    return [
        {
            "item_id": item["item_id"],
            "description": item["description"],
            "rfq_uom": item["rfq_uom"],
            "quoted_uom": item["quoted_uom"],
            "pack_size": item["pack_size"],
        }
        for item in items
        if item["uom_conversion_required"]
    ]