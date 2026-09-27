UOM_ALIASES = {
    "pc": "pcs",
    "pcs": "pcs",
    "piece": "pcs",
    "pieces": "pcs",

    "box": "box",
    "boxes": "box",

    "roll": "roll",
    "rolls": "roll",

    "pack": "pack",
    "packs": "pack",

    "sheet": "sheet",
    "sheets": "sheet",

    "kg": "kg",
    "kgs": "kg",

    "kit": "kit",
    "kits": "kit",
}


def normalize_uom(uom: str) -> str:
    if not uom:
        return ""

    value = uom.strip().lower()

    return UOM_ALIASES.get(value, value)