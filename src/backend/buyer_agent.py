from langchain.agents import create_agent
from src.backend.llm_config import llm_openai

from src.backend.agent_tools import (
    list_vendors,
    get_items_for_vendor,
    get_questionnaire_for_vendor,
    get_uom_mismatches,
    get_missing_items,
    get_uom_mismatches
)


SYSTEM_PROMPT = """
You are a procurement analysis assistant.

You help buyers analyze vendor quotations stored in the procurement database.

Rules:
1. Always use the available database tools to retrieve actual procurement data.
2. Never invent vendor data, prices, quantities, or questionnaire responses.
3. If information is missing, clearly say that it is missing.
4. When comparing vendors, use the data returned by the tools.
5. Do not assume that different currencies or units are directly comparable.
6. When asked which RFQ items are missing from a vendor quote,
   always use the get_missing_items tool. Do not infer missing
   items by manually comparing item IDs from the quote.
7. For missing RFQ items, always use get_missing_items.
8. For UOM differences, always use get_uom_mismatches.
9. Do not output "[]-" or other list artifacts.

"""


buyer_agent = create_agent(model=llm_openai,
    tools=[
        list_vendors,
        get_items_for_vendor,
        get_questionnaire_for_vendor,
        get_uom_mismatches,
        get_missing_items,
        get_uom_mismatches
    ],
    system_prompt=SYSTEM_PROMPT,
)

question = """
Which RFQ items are quoted by both vendors, and for each of those items
show the vendor, quoted price, currency, and UOM?

Do not convert currencies and do not identify a lower-priced vendor.
I only want the side-by-side quoted values from the database.
"""



def main(question):
    result = buyer_agent.invoke({"messages" : [{"role":"user", "content": question}]} )
    messages = result["messages"][-1]
    for block in messages.content:
        if block["type"] =="text":
            result = block["text"]
    return result


