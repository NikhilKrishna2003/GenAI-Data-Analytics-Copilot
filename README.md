# GenAI Data Analytics Copilot

A GenAI-powered assistant that converts natural language questions into SQL queries and performs automated analytics on uploaded CSV datasets.

This system enables users to analyze structured data simply by asking questions in natural language. The system automatically understands the dataset schema, generates structured analytical plans using an LLM, builds safe SQL queries, executes them, and returns insights instantly.

---

## Project Demo

### Application Interface

![Application Interface](Images/interface.png)

Users upload a dataset and ask analytical questions in natural language.

---

## Example Question

User asks:

```
highest number of sellers from which state
```

---

## Structured Query Plan

The system converts the natural language question into a structured analytical plan.

![Structured Query Plan](Images/structured_query_plan.png)

Example generated plan:

```
{
  "aggregations": [
    {
      "function": "count",
      "column": "*",
      "alias": "row_count"
    }
  ],
  "group_by": ["seller_state"],
  "order_by": [
    {
      "column": "row_count",
      "direction": "desc"
    }
  ]
}
```

---

## Generated SQL

The system converts the structured plan into safe SQL.

![Generated SQL](Images/generated_sql.png)

Example SQL:

```
SELECT seller_state,
       COUNT(*) AS row_count
FROM sellers
GROUP BY seller_state
ORDER BY row_count DESC
LIMIT 10;
```

---

## Query Results

The SQL query is executed using DuckDB and results are displayed instantly.

![Query Result](Images/query_result.png)

Example output:

| seller_state | row_count |
| ------------ | --------- |
| SP           | 1849      |
| PR           | 349       |
| MG           | 244       |
| SC           | 190       |
| RJ           | 171       |

---

## Downloadable Outputs

The system also generates downloadable analytics outputs.

![Download Outputs](Images/download_outputs.png)

Generated files include:

* generated_sql.sql
* query_result.csv
* final_report.txt

---

## Key Features

• Natural Language Data Analytics
• Automatic CSV dataset analysis
• Schema understanding using embeddings
• LLM-based query planning
• Intent enhancement for analytical questions
• Safe SQL query generation
• Fast query execution using DuckDB
• Downloadable analytics outputs

---

## Technologies Used

Python
LangChain
Transformers
Sentence Transformers
DuckDB
Pandas
Gradio

---

## System Architecture

```
User Question
      │
      ▼
Schema Detection
      │
      ▼
Embedding-based Schema Retrieval
      │
      ▼
LLM Query Planner
      │
      ▼
Intent Enhancer
      │
      ▼
SQL Builder
      │
      ▼
DuckDB Query Engine
      │
      ▼
Results + Reports
```

---

## Installation

Create virtual environment

```
python -m venv venv
```

Activate environment

```
venv\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

Run application

```
python app.py
```

Open browser

```
http://127.0.0.1:7860
```

---

## Real World Applications

This system can be used for:

• Business analytics dashboards
• Internal company data copilots
• Customer analytics systems
• Self-service business intelligence tools
• Automated SQL analytics assistants

---

## Future Improvements

• Multi-table dataset support
• Automatic visualizations
• Support for Excel and PDF datasets
• Cloud deployment
• API integration
