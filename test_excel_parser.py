from src.backend.hybrid_excel_parser import extract_text_tables
from src.backend.procurement_table_parser import parse_html_table
from src.backend.normalize_vendor import normalize_vendor_a
from src.backend.validate_vendor import validate_vendor_quote
from src.backend.comparison import build_comparison
from src.backend.vendor_quotes import VendorQuoteCollection

file_path = r"D:\Aerchain\data\Vendor_A_Quote.xlsx"
from src.backend.rfq import RFQ_ITEM_IDS
with open(file_path, "rb") as f:
    file_bytes = f.read()
from src.backend.rfq import RFQ_ITEMS

print("\nRFQ ITEMS")
print(f"Total items: {len(RFQ_ITEMS)}")
print("First item:", RFQ_ITEMS[0])
print("Last item:", RFQ_ITEMS[-1])

raw_elements = extract_text_tables(file_bytes)

tables = []

for element in raw_elements:

    html = getattr(element.metadata, "text_as_html", None)

    if html:
        rows = parse_html_table(html)

        if rows:
            tables.append(rows)


vendor_info = tables[0]
items = tables[1]
questionnaire = tables[2]

normalized_vendor_quote = normalize_vendor_a(
    vendor_info,
    items
)

vendor_quote = normalized_vendor_quote.vendor
normalized_items = normalized_vendor_quote.items



print("\nNORMALIZED VENDOR")
print(vendor_quote)

print("\nNORMALIZED FIRST ITEM")
print(normalized_items[0])

print("\nNORMALIZED LAST ITEM")
print(normalized_items[-1])



validation_result = validate_vendor_quote(
    vendor_quote,
    normalized_items,
    RFQ_ITEM_IDS
)

normalized_vendor_quote.validation_passed = validation_result.passed
normalized_vendor_quote.validation_issues = validation_result.issues

collection = VendorQuoteCollection()

collection.add(normalized_vendor_quote)

print("\nVENDOR COLLECTION")
print(f"Total vendors: {len(collection.get_all())}")
print(f"Vendor: {collection.get_all()[0].vendor.vendor_name}")

print("\nVALIDATION RESULT")

print(f"Passed: {validation_result.passed}")
print(f"Missing items: {validation_result.missing_items}")
print(f"Unexpected items: {validation_result.unexpected_items}")

if validation_result.issues:
    print("\nIssues:")

    for issue in validation_result.issues:
        print(f"❌ {issue}")
else:
    print("✅ Vendor quote passed validation.")

comparison_rows = build_comparison(
        collection.get_all()
)

print("\nCOMPARISON ROW")
print(comparison_rows[0])