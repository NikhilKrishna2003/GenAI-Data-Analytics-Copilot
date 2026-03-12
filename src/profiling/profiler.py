import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict:
    profile = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": []
    }

    for col in df.columns:
        series = df[col]
        non_null = int(series.notna().sum())
        null_count = int(series.isna().sum())
        dtype = str(series.dtype)

        sample_values = (
            series.dropna()
            .astype(str)
            .head(5)
            .tolist()
        )

        profile["columns"].append({
            "name": col,
            "dtype": dtype,
            "non_null_count": non_null,
            "null_count": null_count,
            "sample_values": sample_values
        })

    return profile