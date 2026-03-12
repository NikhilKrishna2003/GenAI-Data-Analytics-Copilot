import re


BLOCKED_KEYWORDS = [
    "drop", "delete", "update", "insert", "alter",
    "truncate", "replace", "attach", "copy", "create"
]


def validate_sql(sql: str, allowed_columns: list, table_name: str) -> tuple[bool, str]:
    sql_lower = sql.lower().strip()

    if not sql_lower.startswith("select"):
        return False, "Only SELECT queries are allowed."

    for keyword in BLOCKED_KEYWORDS:
        if keyword in sql_lower:
            return False, f"Blocked keyword found: {keyword}"

    if table_name.lower() not in sql_lower:
        return False, "Generated SQL does not reference the expected table."

    identifiers = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", sql)
    allowed_set = set([c.lower() for c in allowed_columns] + [
        table_name.lower(), "select", "from", "where", "group", "by", "order",
        "limit", "as", "count", "sum", "avg", "min", "max", "distinct",
        "desc", "asc", "and", "or"
    ])

    for token in identifiers:
        if token.lower() not in allowed_set and not token.isdigit():
            pass

    return True, "SQL is valid."