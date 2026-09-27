from dataclasses import dataclass


@dataclass
class RFQItem:
    item_id: str
    description: str
    quantity: float
    uom: str


RFQ_ITEMS = [
    RFQItem("ITM-001", "Corrugated shipping carton 5-ply", 1200, "pcs"),
    RFQItem("ITM-002", "Stretch film 500mm x 23 micron", 350, "roll"),
    RFQItem("ITM-003", "Pallet wooden 1200 x 1000mm", 600, "pcs"),
    RFQItem("ITM-004", "Safety gloves nitrile, L", 180, "box"),
    RFQItem("ITM-005", "Safety helmet industrial, white", 150, "pcs"),
    RFQItem("ITM-006", "Barcode label 100 x 50mm", 240, "roll"),
    RFQItem("ITM-007", "Thermal transfer ribbon 110mm x 300m", 90, "roll"),
    RFQItem("ITM-008", "Packing tape 48mm x 65m", 500, "roll"),
    RFQItem("ITM-009", "Plastic strapping 16mm", 220, "kg"),
    RFQItem("ITM-010", "Strapping buckle 16mm", 3000, "pcs"),
    RFQItem("ITM-011", "Bubble wrap 1m x 50m", 80, "roll"),
    RFQItem("ITM-012", "Foam sheet 5mm, 1m x 2m", 400, "sheet"),
    RFQItem("ITM-013", "Cable tie 200mm black", 250, "pack"),
    RFQItem("ITM-014", "Pallet corner protector", 1800, "pcs"),
    RFQItem("ITM-015", "Desiccant silica gel 50g", 1000, "pack"),
    RFQItem("ITM-016", "Industrial marker black", 300, "pcs"),
    RFQItem("ITM-017", "A4 thermal paper roll", 100, "roll"),
    RFQItem("ITM-018", "Hand pallet truck 2.5T", 12, "pcs"),
    RFQItem("ITM-019", "Warehouse safety cone 750mm", 80, "pcs"),
    RFQItem("ITM-020", "Reflective safety vest", 120, "pcs"),
    RFQItem("ITM-021", "MS storage bin 400 x 300 x 200mm", 90, "pcs"),
    RFQItem("ITM-022", "Plastic tote box 600 x 400 x 320mm", 120, "pcs"),
    RFQItem("ITM-023", "Anti-static ESD bag 200 x 300mm", 150, "pack"),
    RFQItem("ITM-024", "Packing paper kraft 80 GSM", 300, "kg"),
    RFQItem("ITM-025", "Poly mailer 300 x 400mm", 2500, "pcs"),
    RFQItem("ITM-026", "Warehouse barcode scanner, handheld", 25, "pcs"),
    RFQItem("ITM-027", "Label printer 4-inch thermal", 10, "pcs"),
    RFQItem("ITM-028", "USB-C industrial tablet 10-inch", 15, "pcs"),
    RFQItem("ITM-029", "Forklift seat belt replacement kit", 20, "kit"),
    RFQItem("ITM-030", "LED warehouse light 100W", 60, "pcs"),
]


RFQ_ITEM_IDS = [
    item.item_id
    for item in RFQ_ITEMS
]