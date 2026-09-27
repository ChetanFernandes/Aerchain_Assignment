from src.backend.uom import normalize_uom


test_values = [
    "pcs",
    "PC",
    "pieces",
    "Pcs",
    "boxes",
    "rolls",
    "packs",
    "kgs",
    "kits",
]


for value in test_values:
    print(f"{value:10} -> {normalize_uom(value)}")