import streamlit as st
from src.backend.hybrid_excel_parser import extract_text_tables
from src.backend.procurement_table_parser import parse_html_table
from src.backend.normalize_vendor import normalize_vendor
import streamlit as st
from src.backend.validate_vendor import validate_vendor_quote
from src.backend.rfq import RFQ_ITEM_IDS
from src.backend.database import (initialize_database, save_normalized_vendor,)
from src.backend.database import (initialize_database, save_normalized_vendor, save_questionnaire,)
import requests
from src.backend.buyer_agent import buyer_agent


st.set_page_config(page_title="Aerchain Procurement AI", layout="wide",)

initialize_database()

st.title("Aerchain Procurement AI")

st.subheader("RFQ Comparison")

st.info(
    "Upload vendor quotations and analyze them using AI."
)

uploaded_files = st.file_uploader(
    "Upload vendor quotations",
    type=["xlsx"],
    accept_multiple_files=True,
)


if uploaded_files:

    for file in uploaded_files:

        st.write(f"{file.name}")

        file_bytes = file.getvalue()

        if file.name.lower().endswith(".xlsx"):

            # 1. Extract
            elements = extract_text_tables(file_bytes)

            st.success(
                f"Extracted {len(elements)} table element(s)"
            )

            # 2. Show extracted tables
            for i, element in enumerate(elements, start=1):

                st.write(f"### Extracted Table {i}")

                html = getattr(
                    element.metadata,
                    "text_as_html",
                    None,
                )

                if html:
                    st.markdown(
                        html,
                        unsafe_allow_html=True,
                    )

            # 3. Parse tables
            tables = []

            for element in elements:

                html = getattr(
                    element.metadata,
                    "text_as_html",
                    None,
                )

                if html:

                    rows = parse_html_table(html)

                    if rows:
                        tables.append(rows)

            st.write("DEBUG VENDOR DATA:", tables[0])

            # 4. Normalize
            if len(tables) >= 2:

                vendor_info = tables[0]
                items = tables[1]
                print("SENDING TO NORMALIZE:", vendor_info)
                normalized_vendor_quote = normalize_vendor(
                    vendor_info,
                    items,
                )

            

                validation_result = validate_vendor_quote(
                    normalized_vendor_quote.vendor,
                    normalized_vendor_quote.items,
                    RFQ_ITEM_IDS,
                )

                normalized_vendor_quote.validation_passed = validation_result.passed
                normalized_vendor_quote.validation_issues = validation_result.issues



                vendor_id = save_normalized_vendor(normalized_vendor_quote)

                if len(tables) >= 3:

                    questionnaire_rows = tables[2]

                    save_questionnaire(
                        vendor_id,
                        questionnaire_rows
                    )

                    st.success(
                        f"Questionnaire saved for Vendor ID: {vendor_id}"
                    )

                st.success(f"Vendor saved to database. Vendor ID: {vendor_id}")


                if validation_result.passed:
                    st.success(
                        f"Validation Passed — "
                        f"{len(normalized_vendor_quote.items)}/30 items matched"
                    )
                else:
                    st.warning("Buyer Review Required")

                    for issue in validation_result.issues:
                        st.write(f"• {issue}")

                st.success(
                    f"Normalized "
                    f"{len(normalized_vendor_quote.items)} "
                    f"quote items"
                )

          



                # 6. Show normalized items
                st.write("### Normalized Items")

                normalized_rows = []

                for item in normalized_vendor_quote.items:

                    normalized_rows.append(
                        {
                            "Item ID": item.item_id,
                            "Buyer_item_Description": item.description,
                            "Buyer_requested_RFQ Qty": item.rfq_qty,
                            "Buyer_RFQ_UOM": item.rfq_uom,
                            "Vendor_Quoted_UOM": item.quoted_uom,
                            "Vendor_Quoted_Unit_Price": item.unit_price,
                            "Vendor_Quoted_Currency": item.currency,
                            "Lead Time": item.lead_time_days,
                        }
                    )

                st.dataframe(normalized_rows, use_container_width=True)

            else:

                st.error("Could not find the expected vendor and quote tables.")

st.divider()
st.subheader(" Buyer AI Analyst")

question = st.text_area(
    "Ask a procurement question",
    placeholder="Example: Which items are missing from each vendor?"
)

if st.button("Analyze") and question.strip():

    #with st.spinner("Analyzing procurement data..."):
    
        #response = send_payload(question)

        #if "error" in response:
            #st.error(response["error"])
        #else:
            #st.write(response)

    with st.spinner("Analyzing procurement data..."):

        result = buyer_agent.invoke(
            {
                "messages": [
                    {
                       "role": "user",
                        "content": question,
                    }
                ]
            }
        )

    final_message = result["messages"][-1]

    response_text = ""
    for block in final_message.content:
        if block["type"] == "text":
            response_text += block["text"]
            st.markdown("### Analysis")
            st.write(response_text)
            


  


