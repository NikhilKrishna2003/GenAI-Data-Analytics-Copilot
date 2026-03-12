import re


AGGREGATE_WORDS = {
    "count": ["count", "how many", "number of", "total"],
    "top_n": ["top", "highest", "largest", "most", "best"],
    "average": ["average", "avg", "mean"],
    "sum": ["sum", "total sum"],
    "min_max": ["minimum", "maximum", "min", "max", "lowest", "highest"],
    "distinct": ["unique", "distinct", "different"],
    "group": ["per", "by each", "group by", "distribution", "across", "by "]
}


def contains_any(text: str, words: list[str]) -> bool:
    text = text.lower()
    return any(w in text for w in words)


def extract_limit(question: str, default: int = 10) -> int:
    match = re.search(r"\btop\s+(\d+)\b", question.lower())
    if match:
        return int(match.group(1))
    return default


def choose_best_dimension(columns: list[str], question: str) -> str | None:
    q = question.lower()

    for col in columns:
        c = col.lower()
        if "state" in q and "state" in c:
            return col
        if "city" in q and "city" in c:
            return col
        if "category" in q and "category" in c:
            return col
        if "score" in q and "score" in c:
            return col
        if "review" in q and "score" in c:
            return col
        if "zip" in q and "zip" in c:
            return col
    return columns[0] if columns else None


def choose_best_measure(columns: list[str], question: str) -> str | None:
    q = question.lower()

    numeric_keywords = [
        "weight", "length", "height", "width", "score",
        "qty", "quantity", "price", "amount", "count"
    ]

    for col in columns:
        c = col.lower()
        if any(k in q and k in c for k in numeric_keywords):
            return col

    for col in columns:
        c = col.lower()
        if any(k in c for k in numeric_keywords):
            return col

    return None


def enhance_plan(question: str, plan: dict, allowed_columns: list[str]) -> dict:
    q = question.lower().strip()

    plan = plan or {}
    intent = plan.get("intent", "select_preview")
    columns_needed = plan.get("columns_needed", []) or []
    aggregations = plan.get("aggregations", []) or []
    filters = plan.get("filters", []) or []
    group_by = plan.get("group_by", []) or []
    order_by = plan.get("order_by", []) or []
    limit = plan.get("limit", 10) or 10

    limit = extract_limit(q, limit)

    best_dim = choose_best_dimension(allowed_columns, q)
    best_measure = choose_best_measure(allowed_columns, q)

    if contains_any(q, AGGREGATE_WORDS["count"]):
        if contains_any(q, AGGREGATE_WORDS["group"]) or best_dim:
            if not group_by and best_dim and ("per " in q or " by " in q or "distribution" in q or "highest" in q or "top" in q):
                group_by = [best_dim]

            if group_by and not aggregations:
                aggregations = [{"function": "count", "column": "*", "alias": "row_count"}]
                intent = "group_aggregate"

                if not order_by and contains_any(q, AGGREGATE_WORDS["top_n"]):
                    order_by = [{"column": "row_count", "direction": "desc"}]
            elif not group_by:
                intent = "count_rows"
                aggregations = [{"function": "count", "column": "*", "alias": "row_count"}]

    if contains_any(q, AGGREGATE_WORDS["distinct"]):
        target_col = best_dim or (columns_needed[0] if columns_needed else None)
        if target_col:
            intent = "distinct_count"
            aggregations = [{"function": "count", "column": f"DISTINCT {target_col}", "alias": "unique_count"}]
            group_by = []
            order_by = []

    if contains_any(q, AGGREGATE_WORDS["top_n"]):
        if best_dim and not group_by:
            group_by = [best_dim]
        if not aggregations:
            aggregations = [{"function": "count", "column": "*", "alias": "row_count"}]
        if not order_by:
            alias = aggregations[0].get("alias", "row_count")
            order_by = [{"column": alias, "direction": "desc"}]
        intent = "top_n"

    if contains_any(q, AGGREGATE_WORDS["average"]):
        if best_measure:
            intent = "average"
            aggregations = [{"function": "avg", "column": best_measure, "alias": f"avg_{best_measure}"}]
            if best_dim and ("per " in q or " by " in q):
                group_by = [best_dim]
                intent = "group_aggregate"

    if contains_any(q, AGGREGATE_WORDS["sum"]):
        if best_measure:
            intent = "sum"
            aggregations = [{"function": "sum", "column": best_measure, "alias": f"sum_{best_measure}"}]
            if best_dim and ("per " in q or " by " in q):
                group_by = [best_dim]
                intent = "group_aggregate"

    if contains_any(q, AGGREGATE_WORDS["min_max"]):
        if best_measure and not aggregations:
            fn = "max" if ("max" in q or "highest" in q or "largest" in q) else "min"
            intent = "min_max"
            aggregations = [{"function": fn, "column": best_measure, "alias": f"{fn}_{best_measure}"}]

    if intent == "select_preview" and (
        contains_any(q, AGGREGATE_WORDS["count"])
        or contains_any(q, AGGREGATE_WORDS["top_n"])
        or contains_any(q, AGGREGATE_WORDS["average"])
        or contains_any(q, AGGREGATE_WORDS["sum"])
        or contains_any(q, AGGREGATE_WORDS["distinct"])
    ):
        if best_dim:
            group_by = [best_dim]
            aggregations = [{"function": "count", "column": "*", "alias": "row_count"}]
            order_by = [{"column": "row_count", "direction": "desc"}]
            intent = "group_aggregate"

    return {
        "intent": intent,
        "columns_needed": columns_needed,
        "aggregations": aggregations,
        "filters": filters,
        "group_by": group_by,
        "order_by": order_by,
        "limit": limit
    }