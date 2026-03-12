import os
import re
import uuid
import tempfile

def sanitize_table_name(filename: str) -> str:
    name = os.path.splitext(os.path.basename(filename))[0].lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    if not name:
        name = "uploaded_table"
    if name[0].isdigit():
        name = f"table_{name}"
    return name


def create_output_paths():
    run_id = uuid.uuid4().hex[:8]

    base_dir = os.path.join(tempfile.gettempdir(), "project_output", run_id)
    os.makedirs(base_dir, exist_ok=True)

    sql_path = os.path.join(base_dir, "generated_sql.sql")
    data_path = os.path.join(base_dir, "query_result.csv")
    report_path = os.path.join(base_dir, "final_report.txt")

    return sql_path, data_path, report_path
