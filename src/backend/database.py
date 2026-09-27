import sqlite3
from pathlib import Path


# -----------------------------------------
# Database location
# -----------------------------------------

DB_PATH = Path("data/aerchain.db")


# -----------------------------------------
# Get database connection
# -----------------------------------------

def get_connection():

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# -----------------------------------------
# Initialize database
# -----------------------------------------

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # -----------------------------------------
    # Vendors
    # -----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT NOT NULL,
            quote_ref TEXT,
            quote_date TEXT,
            currency TEXT,
            validity TEXT,
            payment_terms TEXT,
            delivery_terms TEXT,
            gst TEXT
        )
    """)

    # -----------------------------------------
    # Quote Items
    # -----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quote_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vendor_id INTEGER NOT NULL,

            item_id TEXT NOT NULL,
            description TEXT,

            rfq_qty REAL,
            rfq_uom TEXT,

            quoted_uom TEXT,
            unit_price REAL,
            currency TEXT,

            lead_time_days INTEGER,

            uom_conversion_required INTEGER DEFAULT 0,
            currency_normalization_required INTEGER DEFAULT 0,

            FOREIGN KEY (vendor_id)
                REFERENCES vendors(vendor_id)
        )
    """)

    try:
        cursor.execute("""
            ALTER TABLE quote_items
            ADD COLUMN pack_size REAL
        """)
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # -----------------------------------------
    # Questionnaire
    # -----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questionnaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vendor_id INTEGER NOT NULL,

            question TEXT NOT NULL,
            response TEXT,
            notes TEXT,

            FOREIGN KEY (vendor_id)
                REFERENCES vendors(vendor_id)
        )
    """)

    # -----------------------------------------
    # Evidence
    # -----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vendor_id INTEGER,

            item_id TEXT,

            source_file TEXT NOT NULL,
            source_text TEXT,

            FOREIGN KEY (vendor_id)
                REFERENCES vendors(vendor_id)
        )
    """)

    connection.commit()

    connection.close()


# -----------------------------------------
# Save vendor
# -----------------------------------------

def save_vendor(vendor):

    connection = get_connection()

    cursor = connection.cursor()

    # Check whether this quote already exists
    cursor.execute("""
        SELECT vendor_id
        FROM vendors
        WHERE vendor_name = ?
          AND quote_ref = ?
    """, (
        vendor.vendor_name,
        vendor.quote_ref,
    ))

    existing = cursor.fetchone()

    if existing:

        vendor_id = existing["vendor_id"]

        connection.close()

        return vendor_id

    # Insert new vendor quote
    cursor.execute("""
        INSERT INTO vendors (
            vendor_name,
            quote_ref,
            quote_date,
            currency,
            validity,
            payment_terms,
            delivery_terms,
            gst
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        vendor.vendor_name,
        vendor.quote_ref,
        vendor.quote_date,
        vendor.currency,
        vendor.validity,
        vendor.payment_terms,
        vendor.delivery_terms,
        vendor.gst,
    ))

    vendor_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return vendor_id


# -----------------------------------------
# Save quote items
# -----------------------------------------

def save_quote_items(vendor_id, items):

    connection = get_connection()
    cursor = connection.cursor()

    # Remove previous quote items for this vendor
    cursor.execute("""
        DELETE FROM quote_items
        WHERE vendor_id = ?
    """, (vendor_id,))

    # Insert the latest quote
    for item in items:

        cursor.execute("""
            INSERT INTO quote_items (
                vendor_id,
                item_id,
                description,
                rfq_qty,
                rfq_uom,
                quoted_uom,
                unit_price,
                currency,
                lead_time_days,
                uom_conversion_required,
                currency_normalization_required,
                pack_size
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vendor_id,
            item.item_id,
            item.description,
            item.rfq_qty,
            item.rfq_uom,
            item.quoted_uom,
            item.unit_price,
            item.currency,
            item.lead_time_days,
            int(item.uom_conversion_required),
            int(item.currency_normalization_required),
            item.pack_size
        ))

    connection.commit()
    connection.close()


# -----------------------------------------
# Read vendors
# -----------------------------------------

def get_vendors():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM vendors
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# -----------------------------------------
# Read quote items for vendor
# -----------------------------------------

def get_vendor_items(vendor_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM quote_items
        WHERE vendor_id = ?
    """, (vendor_id,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def save_normalized_vendor(normalized_vendor_quote):

    vendor_id = save_vendor(
        normalized_vendor_quote.vendor
    )

    save_quote_items(
        vendor_id,
        normalized_vendor_quote.items
    )

    return vendor_id

def save_questionnaire(vendor_id, questionnaire_rows):

    connection = get_connection()
    cursor = connection.cursor()

    # Remove previous questionnaire responses for this vendor
    cursor.execute("""
        DELETE FROM questionnaire
        WHERE vendor_id = ?
    """, (vendor_id,))

    # Insert the latest questionnaire responses
    for row in questionnaire_rows:

        question = row.get("Question", "")
        response = row.get("Response", "")
        notes = row.get("Notes", "")

        cursor.execute("""
            INSERT INTO questionnaire (
                vendor_id,
                question,
                response,
                notes
            )
            VALUES (?, ?, ?, ?)
        """, (
            vendor_id,
            question,
            response,
            notes,
        ))

    connection.commit()
    connection.close()

def get_questionnaire(vendor_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM questionnaire
        WHERE vendor_id = ?
    """, (vendor_id,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]