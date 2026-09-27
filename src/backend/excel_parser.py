from unstructured.partition.xlsx import partition_xlsx
from src.backend.utilis import * 
from src.logger_config import log
import os
import tempfile
# Extract only text + tables (no images).

def extract_text_tables(file_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(file_bytes)
            tmp.flush()                  
            tmp_path = tmp.name
        log.info(f"Processing temp excel: {tmp_path}")
        raw_excel_elements =  partition_xlsx( 
                            filename = tmp_path,
                            find_subtable = True,
                            include_header = False,
                            infer_table_structure = True,
                            starting_page_number = 1)
    
        return raw_excel_elements
    except Exception:
        log.exception("Extracting excel elements failed")
        return []
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        log.info(f"Tmp File removed: {tmp_path}")











    






    