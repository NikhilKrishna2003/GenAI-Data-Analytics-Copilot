import duckdb
import pandas as pd


class SQLExecutor:
    def __init__(self, df: pd.DataFrame, table_name: str):
        self.table_name = table_name
        self.con = duckdb.connect(database=":memory:")
        self.con.register("uploaded_df", df)
        self.con.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM uploaded_df"
        )

    def execute(self, sql: str) -> pd.DataFrame:
        return self.con.execute(sql).fetchdf()

    def describe(self) -> pd.DataFrame:
        return self.con.execute(f"DESCRIBE {self.table_name}").fetchdf()