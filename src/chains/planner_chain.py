import json
from transformers import pipeline


class QueryPlanner:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device_map="auto"
        )

    def build_prompt(self, question: str, relevant_columns: list, table_name: str) -> str:
        column_text = "\n".join(
            [f"- {col['column_name']}: {col['text']}" for col in relevant_columns]
        )

        return f"""
You are a data analyst query planner.

Your job is to convert the user's analytical question into a structured JSON plan.
Return only valid JSON.

Important rules:
- If the user asks "how many", "count", "top", "highest", "most", "distribution", "per X", or "by X", prefer an aggregate query, not a preview query.
- Use group_aggregate for grouped counts, averages, sums, min/max.
- Use top_n when the user asks for highest/top/most.
- Use distinct_count for unique/distinct counts.
- Use average for AVG(column).
- Use sum for SUM(column).
- Use count_rows for total row count.
- Only use columns from the provided schema.
- Do not invent columns.
- Do not write SQL.
- Return only JSON.

Allowed intents:
- select_preview
- count_rows
- distinct_count
- group_aggregate
- top_n
- average
- sum
- min_max
- filter_aggregate
- comparison

Table name:
{table_name}

Relevant columns:
{column_text}

User question:
{question}

Return JSON in this format:
{{
  "intent": "",
  "columns_needed": [],
  "aggregations": [],
  "filters": [],
  "group_by": [],
  "order_by": [],
  "limit": 10
}}
"""

    def plan(self, question: str, relevant_columns: list, table_name: str) -> dict:
        prompt = self.build_prompt(question, relevant_columns, table_name)

        output = self.generator(
            prompt,
            max_new_tokens=220,
            do_sample=False,
            return_full_text=False
        )

        raw = output[0]["generated_text"].strip()

        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            raw_json = raw[start:end]
            return json.loads(raw_json)
        except Exception:
            return {
                "intent": "select_preview",
                "columns_needed": [],
                "aggregations": [],
                "filters": [],
                "group_by": [],
                "order_by": [],
                "limit": 10
            }