# AI Data Analyst Copilot V2

A GenAI-powered data analyst assistant that converts natural language questions into SQL queries for uploaded CSV datasets.

## Features

- Upload any CSV dataset
- Automatic schema profiling
- Embedding-based schema retrieval
- LLM-based structured query planning
- Intent enhancement for analytical questions
- Safe SQL generation
- Query execution using DuckDB
- Downloadable SQL, CSV, and report outputs

## Supported Query Types

- Count rows
- Distinct count
- Grouped count
- Top N
- Highest / most
- Average
- Sum
- Min / Max
- Simple grouped analytics using `per` or `by`

## Installation

Create virtual environment:

```bash
python -m venv venv