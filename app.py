import os
import sys
import json
import pandas as pd
import gradio as gr

sys.path.append(os.path.abspath("."))

from src.profiling.profiler import profile_dataframe
from src.retrieval.schema_index import SchemaRetriever
from src.chains.planner_chain import QueryPlanner
from src.chains.intent_enhancer import enhance_plan
from src.sql.builder import build_sql_from_plan
from src.sql.validator import validate_sql
from src.sql.executor import SQLExecutor
from src.utils.helpers import sanitize_table_name, create_output_paths

planner = QueryPlanner()


def generate_report(question: str, sql: str, result_df: pd.DataFrame) -> str:
    if result_df.empty:
        return f"Question: {question}\n\nSQL: {sql}\n\nNo rows returned."

    return (
        f"Question:\n{question}\n\n"
        f"Generated SQL:\n{sql}\n\n"
        f"Result Preview:\n{result_df.head(10).to_string(index=False)}\n\n"
        f"Rows Returned: {len(result_df)}\n"
        f"Columns Returned: {', '.join(result_df.columns.astype(str).tolist())}\n"
    )


def analyze(file_obj, question: str):
    if file_obj is None:
        return "Please upload a CSV file.", None, None, None, None, None

    if not question or not question.strip():
        return "Please enter a question.", None, None, None, None, None

    try:
        df = pd.read_csv(file_obj.name)
        table_name = sanitize_table_name(file_obj.name)

        profiler_output = profile_dataframe(df)

        retriever = SchemaRetriever()
        retriever.build_index(profiler_output)
        relevant_columns = retriever.retrieve(question, top_k=5)

        executor = SQLExecutor(df, table_name)
        schema_df = executor.describe()
        allowed_columns = schema_df["column_name"].astype(str).tolist()

        raw_plan = planner.plan(question, relevant_columns, table_name)
        plan = enhance_plan(question, raw_plan, allowed_columns)

        sql = build_sql_from_plan(plan, table_name)

        is_valid, msg = validate_sql(sql, allowed_columns, table_name)
        if not is_valid:
            return (
                f"SQL validation failed: {msg}",
                schema_df,
                json.dumps(plan, indent=2),
                sql,
                None,
                None,
            )

        result_df = executor.execute(sql)
        report = generate_report(question, sql, result_df)

        sql_path, data_path, report_path = create_output_paths()

        with open(sql_path, "w", encoding="utf-8") as f:
            f.write(sql)

        result_df.to_csv(data_path, index=False)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return (
            "Analysis completed successfully.",
            schema_df,
            json.dumps(plan, indent=2),
            sql,
            result_df,
            [sql_path, data_path, report_path],
        )

    except Exception as e:
        return f"Error: {str(e)}", None, None, None, None, None


with gr.Blocks(title="GenAI Data Analytics Copilot") as demo:
    gr.Markdown("# GenAI Data Analytics Copilot")
    gr.Markdown(
        "Upload a CSV, ask a question in natural language, and get a safe SQL query, "
        "results table, and downloadable outputs."
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload CSV", file_types=[".csv"])
            question_input = gr.Textbox(
                label="Ask a question",
                lines=3,
                placeholder="Example: Count sellers per state",
            )
            run_btn = gr.Button("Run Analysis", variant="primary")
            status_output = gr.Textbox(label="Status", interactive=False)

        with gr.Column(scale=2):
            schema_output = gr.Dataframe(label="Detected Schema")
            plan_output = gr.Textbox(label="Structured Query Plan", lines=14)
            sql_output = gr.Code(label="Generated SQL", language="sql")
            result_output = gr.Dataframe(label="Query Result")
            files_output = gr.Files(label="Download Outputs")

    run_btn.click(
        fn=analyze,
        inputs=[file_input, question_input],
        outputs=[
            status_output,
            schema_output,
            plan_output,
            sql_output,
            result_output,
            files_output,
        ],
    )

if __name__ == "__main__":
    demo.launch()