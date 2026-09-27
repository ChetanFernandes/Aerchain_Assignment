# Aerchain Procurement AI --- "Kill the Quote Spreadsheet"

## 1. Overview

This prototype demonstrates an AI-native procurement workflow for
comparing vendor quotations against a 30-line RFQ.

The buyer can upload vendor quotation spreadsheets, have the data
extracted and normalized into a common procurement structure, validate
the quote, identify missing lines and UOM ambiguities, persist the
results, and then ask natural-language questions over the stored
procurement data.

The core design principle is **buyer trust**: the system does not
silently invent missing data, silently normalize ambiguous units, or
blindly compare different currencies.

------------------------------------------------------------------------

## 2. Problem Being Solved

Traditional procurement comparison often requires a buyer to manually
consolidate vendor responses into a spreadsheet.

The prototype addresses the following workflow:

1.  Start with a 30-item RFQ.
2.  Receive quotations from multiple vendors.
3.  Extract vendor and line-item information.
4.  Normalize different representations into a common structure.
5.  Validate each quotation against the RFQ.
6.  Identify missing RFQ lines.
7.  Detect UOM differences and pack-size ambiguity.
8.  Preserve questionnaire/commercial information.
9.  Store normalized data.
10. Let a buyer interrogate the actual stored data using natural
    language.
11. Surface uncertainty and buyer-review requirements instead of
    presenting false certainty.

------------------------------------------------------------------------

## 3. Current Demo Scope

The working demo contains five vendor quotations:

  ------------------------------------------------------------------------
  Vendor                  Quote coverage Currency         Notable edge
                                                          cases
  ---------------- --------------------- ---------------- ----------------
  Nova Industrial                  27/30 USD              Missing RFQ
  Solutions                                               lines; currency
                                                          normalization
                                                          needed for
                                                          comparison

  Apex Packaging &                 30/30 INR              Baseline
  Industrial                                              complete
  Supplies Pvt Ltd                                        quotation

  Orion Packaging                  27/30 INR              Missing lines;
  Solutions                                               `100 pcs/box`
                                                          pack-size
                                                          ambiguity

  Delta Industrial                 25/30 INR              Missing lines;
  Supplies                                                UOM differences

  Evergreen                        19/30 INR/USD          Missing lines;
  Packaging                                               `box of 20`;
  Traders                                                 mixed currency
  ------------------------------------------------------------------------

The prototype currently focuses on the **Excel ingestion path** for the
working Streamlit demonstration.

------------------------------------------------------------------------

## 4. End-to-End Architecture

``` text
                    ┌─────────────────────────┐
                    │       Streamlit UI      │
                    │  Upload + Buyer Analyst │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Excel Extraction     │
                    │  unstructured/openpyxl  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Table Parsing          │
                    │ Vendor / Items / Q&A     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Normalization + UOM     │
                    │ Pack-size detection     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Validation         │
                    │ Missing / invalid / UOM │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       SQLite DB          │
                    │ Quotes / Items / Q&A     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Buyer AI Agent      │
                    │ LangChain + OpenAI LLM   │
                    └─────────────────────────┘
```

For the final demo, the Streamlit application directly invokes the Buyer
AI Agent. The earlier FastAPI layer was bypassed to keep the hosted
prototype simple and self-contained.

------------------------------------------------------------------------

## 5. What Was Built

### 5.1 RFQ definition

A 30-line RFQ is maintained as the authoritative item list.

Each RFQ line contains the item identity and expected procurement basis,
including quantity and UOM.

The RFQ item IDs are used as the reference when validating vendor
responses.

### 5.2 Vendor quote extraction

The current production demo path accepts Excel quotations.

The extraction pipeline uses the existing Excel parsing utilities and
extracts table elements from uploaded workbooks.

The extracted tables are then interpreted as:

-   Vendor/commercial information
-   Quote line items
-   Questionnaire responses

### 5.3 Table parsing

HTML table representations returned by extraction are converted into
Python dictionaries.

The parser handles:

-   Header-based tables
-   Key/value vendor-information tables
-   Empty/invalid table cases

### 5.4 Vendor normalization

Vendor data is normalized into structured models.

The normalization layer extracts fields such as:

-   Vendor name
-   Quote reference
-   Quote date
-   Currency
-   Validity
-   Payment terms
-   Delivery terms
-   GST/tax information

Line items are normalized into:

-   Item ID
-   Description
-   RFQ quantity
-   RFQ UOM
-   Vendor quoted UOM
-   Unit price
-   Currency
-   Lead time
-   UOM conversion requirement
-   Currency normalization requirement
-   Pack size

### 5.5 UOM normalization

Common UOM aliases are normalized, for example:

-   `pc`, `piece`, `pieces` → `pcs`
-   `box`, `boxes` → `box`
-   `roll`, `rolls` → `roll`
-   `pack`, `packs` → `pack`
-   `sheet`, `sheets` → `sheet`
-   `kg`, `kgs` → `kg`
-   `kit`, `kits` → `kit`

The system compares the normalized vendor UOM with the RFQ UOM.

### 5.6 Pack-size detection

The system explicitly detects pack-size expressions such as:

-   `100 pcs/box`
-   `100 pieces per box`
-   `box of 100`
-   `box of 20`

Pack size is stored separately rather than discarded.

Example:

``` text
RFQ UOM:       pcs
Vendor UOM:    100 pcs/box
Pack size:     100
```

This allows the AI to tell the buyer that conversion is required without
pretending that the price basis is known.

### 5.7 Validation

Each normalized vendor quote is validated against the authoritative
30-item RFQ.

Validation checks include:

-   Vendor name present
-   Currency present
-   Missing RFQ item IDs
-   Unexpected item IDs
-   Positive RFQ quantity
-   Unit price present
-   Unit price not negative
-   Vendor UOM present
-   RFQ UOM present
-   UOM mismatch
-   UOM conversion required
-   Pack size available or missing

The result is represented as:

-   Validation passed/failed
-   Validation issues
-   Missing items
-   Unexpected items

### 5.8 Missing-item detection

Missing lines are not inferred by the LLM.

A deterministic tool compares stored vendor item IDs against the
authoritative RFQ item IDs.

The Buyer AI Agent is instructed to use this tool when answering
missing-item questions.

Examples observed in the demo:

``` text
Nova:      ITM-007, ITM-018, ITM-030
Orion:     ITM-003, ITM-011, ITM-020, ITM-026, ITM-029
Delta:     11 missing items
Evergreen: 11 missing items
```

### 5.9 UOM mismatch detection

A deterministic tool retrieves stored items where the vendor UOM differs
from the RFQ UOM.

The tool returns:

-   Item ID
-   Description
-   RFQ UOM
-   Vendor UOM
-   Pack size

The AI uses this information to explain why buyer review is required.

### 5.10 Questionnaire capture

Vendor questionnaire responses are stored separately and exposed to the
Buyer AI Agent.

The demo captures questionnaire information such as:

-   Expedited delivery capability
-   Freight treatment
-   Replacement/claims terms

This allows buyer questions to consider commercial and operational
context in addition to line-item prices.

### 5.11 SQLite persistence

The normalized procurement data is persisted in SQLite.

The database contains structured quote and item information, including
the `pack_size` field needed for UOM ambiguity analysis.

The current working demo has five vendor records.

### 5.12 Buyer AI Agent

The Buyer AI Agent is built using LangChain's agent API and an OpenAI
chat model.

The agent has tools for:

-   Listing vendors
-   Getting vendor items
-   Getting vendor questionnaire responses
-   Getting UOM mismatches
-   Getting missing RFQ items

The system prompt explicitly instructs the agent to:

-   Use actual database tools
-   Never invent procurement data
-   State when information is missing
-   Avoid assuming different currencies or units are directly comparable
-   Use the deterministic missing-item tool
-   Use the deterministic UOM-mismatch tool
-   Format responses clearly in Markdown

### 5.13 Natural-language procurement analysis

The prototype supports buyer questions such as:

``` text
Which items are missing from each vendor?

Show me the UOM mismatches where the vendor specified a pack size.

Compare ITM-001 across all vendors. Do not assume different currencies or UOMs are directly comparable.
```

The agent retrieves actual data and reasons over it rather than
returning hardcoded demo answers.

------------------------------------------------------------------------

## 6. Demonstrated AI / Buyer Trust Scenarios

### Missing RFQ lines

The agent correctly identifies missing items for all five vendors.

### UOM ambiguity

The demo surfaces examples such as:

``` text
Orion:
RFQ: pcs
Vendor: 100 pcs/box
Pack size: 100

Evergreen:
RFQ: pcs
Vendor: box of 20
Pack size: 20
```

The agent explains that the buyer should confirm the price basis before
comparison.

### Currency differences

The demo contains USD, INR and mixed-currency vendor quotes.

The agent does not blindly compare numeric values across currencies.

It explicitly states that currency normalization is required.

### Price-basis ambiguity

For a quote such as `100 pcs/box`, the system can calculate an
arithmetic equivalent only when the stored price basis supports that
calculation, but it still flags the need to confirm that the quoted
price is actually for the box.

### Quantity inconsistency

The ITM-001 comparison exposed different stored RFQ quantities across
vendor quote records.

The AI surfaced this as an additional validation point instead of
silently calculating a misleading total.

### Specification review

The AI can also flag cases where a generic vendor description may need
confirmation against the RFQ specification, such as a required 5-ply
carton.

------------------------------------------------------------------------

## 7. Database / Agent Tool Design

The agent does not receive a giant hardcoded prompt containing all
vendor data.

Instead, it has database-backed tools.

``` text
Buyer question
      ↓
LLM decides which tool(s) are needed
      ↓
Database retrieval
      ↓
Actual vendor data
      ↓
LLM reasoning
      ↓
Buyer-facing answer
```

This keeps the demo grounded in the stored procurement records.

------------------------------------------------------------------------

## 8. What Is Intentionally NOT Built

The assignment mentions multiple vendor-response formats. The current
working demo intentionally scopes these out to move quickly and
demonstrate the core AI loop.

### Not implemented in the final working flow

-   PDF vendor ingestion
-   Word/DOCX vendor ingestion
-   Photographed/rotated quote OCR flow
-   Free-form email ingestion
-   Real SMTP/email integration
-   Production email mailbox integration
-   Full RFx creation workflow
-   Vendor invitation workflow
-   Vendor portal
-   Authentication / authorization
-   Production deployment infrastructure
-   Enterprise-grade database
-   Production secrets/identity architecture
-   Advanced charts
-   Export to Excel/PDF from buyer analysis
-   Full currency-rate service
-   Automatic UOM conversion approval workflow
-   Human-in-the-loop approval UI
-   Production audit/event logging
-   Production observability
-   Multi-user concurrency design

Some generic PDF/DOCX/image extraction utilities were explored
separately, but they were not wired into the final procurement
normalization flow because those outputs require an additional adapter
layer to map extracted content into the vendor/item/questionnaire
schema.

------------------------------------------------------------------------

## 9. Important Design Trade-offs

### No silent UOM conversion

A vendor quoting `100 pcs/box` is not automatically treated as `pcs` for
procurement comparison.

The buyer must confirm the commercial price basis.

### No silent currency conversion

USD and INR values are not treated as directly comparable numeric
values.

A buyer-approved exchange rate or trusted FX service is required before
a normalized financial comparison.

### Missing data remains missing

The system does not invent missing line items, questionnaire responses,
prices or commercial terms.

### Deterministic checks before AI interpretation

Where possible, important facts such as missing RFQ lines and UOM
mismatches are computed by application tools and then interpreted by the
LLM.

This reduces the chance of the model overlooking an important edge case.

------------------------------------------------------------------------

## 10. Technology Stack

-   Python
-   Streamlit
-   LangChain
-   OpenAI chat model
-   SQLite
-   Unstructured
-   OpenPyXL
-   Pandas/dataframe-style UI
-   BeautifulSoup
-   Pydantic/dataclasses for structured models

------------------------------------------------------------------------

## 11. Running Locally

Create/activate the Python environment and install the project
dependencies.

Then run:

``` bash
streamlit run app.py --server.fileWatcherType none
```

The `--server.fileWatcherType none` option is used because the local
Streamlit file watcher can interact poorly with LangGraph's lazy module
attributes in this environment.

The current demo can run end-to-end without the FastAPI layer.

------------------------------------------------------------------------

## 12. Demo Flow

Recommended walkthrough:

1.  Introduce the procurement problem.
2.  Show the 30-item RFQ.
3.  Upload vendor quotations.
4.  Show extraction and normalization.
5.  Show validation.
6.  Show missing RFQ lines.
7.  Show UOM mismatch / pack-size ambiguity.
8.  Show questionnaire information.
9.  Open Buyer AI Analyst.
10. Ask which items are missing from each vendor.
11. Ask for pack-size/UOM ambiguities.
12. Compare ITM-001 across vendors.
13. Show that currency and UOM differences are not silently ignored.
14. Close with the buyer-trust principle.

------------------------------------------------------------------------

## 13. Current Status

### Completed

-   30-item RFQ model
-   Excel quotation ingestion
-   Vendor metadata extraction
-   Line-item extraction
-   Questionnaire extraction
-   Vendor normalization
-   UOM normalization
-   Pack-size detection
-   Missing-line validation
-   UOM mismatch validation
-   Currency normalization flags
-   SQLite persistence
-   Five-vendor demo dataset
-   Database-backed LangChain tools
-   Natural-language buyer analysis
-   Cross-vendor comparison
-   Currency-aware reasoning
-   Buyer-review/uncertainty handling
-   Streamlit end-to-end demo
-   FastAPI dependency bypassed for the final simple demo

### Remaining for submission

-   Push project to GitHub
-   Deploy Streamlit Community Cloud
-   Configure deployment secrets
-   Verify hosted application
-   Record Loom/Google Drive walkthrough
-   Finalize submission document/PPT
-   Share GitHub/live-hosted links

------------------------------------------------------------------------

## 14. Submission Deliverables

The final submission will contain:

1.  **Recorded walkthrough**
    -   Loom or Google Drive
2.  **Live application**
    -   Streamlit Community Cloud URL
3.  **Build document / PPT**
    -   Architecture
    -   What was built
    -   Validation and comparison logic
    -   AI/tool design
    -   Buyer-trust decisions
    -   Scope and trade-offs
    -   What was not built
4.  **Hosted build / repository**
    -   GitHub repository
    -   Streamlit deployment

------------------------------------------------------------------------

## 15. Key Takeaway

The prototype is intentionally focused on the core procurement
intelligence loop:

> **Extract → Normalize → Validate → Store → Retrieve → Reason → Surface
> uncertainty**

The goal is not to make a prettier spreadsheet. The goal is to give a
buyer a trustworthy way to interrogate messy vendor quotations while
making missing data, unit ambiguity, currency differences and other
review points visible.
