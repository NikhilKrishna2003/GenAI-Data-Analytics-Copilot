def build_sql_from_plan(plan: dict, table_name: str) -> str:
    columns_needed = plan.get("columns_needed", [])
    aggregations = plan.get("aggregations", [])
    filters = plan.get("filters", [])
    group_by = plan.get("group_by", [])
    order_by = plan.get("order_by", [])
    limit = plan.get("limit", 10)

    select_parts = []

    # group by dimensions first
    for col in group_by:
        if col not in select_parts:
            select_parts.append(col)

    # aggregation expressions
    for agg in aggregations:
        func = agg.get("function", "").upper()
        col = agg.get("column", "*")
        alias = agg.get("alias", f"{func.lower()}_{str(col).replace(' ', '_')}")

        if str(col).upper().startswith("DISTINCT "):
            select_parts.append(f"COUNT({col}) AS {alias}")
        else:
            select_parts.append(f"{func}({col}) AS {alias}")

    if not select_parts:
        if columns_needed:
            select_parts = columns_needed
        else:
            select_parts = ["*"]

    sql = f"SELECT {', '.join(select_parts)} FROM {table_name}"

    if filters:
        where_clauses = []
        for flt in filters:
            col = flt.get("column")
            op = flt.get("operator", "=")
            val = flt.get("value")

            if isinstance(val, str):
                val = f"'{val}'"
            where_clauses.append(f"{col} {op} {val}")

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

    if group_by:
        sql += " GROUP BY " + ", ".join(group_by)

    if order_by:
        order_clauses = []
        for ob in order_by:
            col = ob.get("column")
            direction = ob.get("direction", "DESC").upper()
            order_clauses.append(f"{col} {direction}")
        sql += " ORDER BY " + ", ".join(order_clauses)

    if limit and (group_by or order_by or select_parts == ["*"] or columns_needed):
        sql += f" LIMIT {int(limit)}"

    return sql + ";"