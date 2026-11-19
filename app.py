from pathlib import Path

import pandas as pd
from datetime import datetime
import sqlite3

#----------------core variables

#paths
repo_path = Path(__file__).resolve().parent
data_path = repo_path/ "data"
cleaned_path = repo_path/ "cleaned"
db_path = cleaned_path / "libray.db"

#input csv
books_input = data_path/ "03_Library Systembook.csv"
system_input = data_path/ "03_Library SystemCustomers.csv"

date_format = "%d/%m/%Y"

book_mask = ["Id","Book checkout", "Book Returned","Books","Days allowed to borrow","Customer ID" ]
system_mask = [ "Customer ID" ,"Customer Name"]

pk_cols_Book = ["Id"]
pk_cols_system = ["Customer ID"]


#--------------fuctions

def load_data(path: Path):
    return pd.read_csv(path, dtype="string")

def check_nulls(df:pd.DataFrame, required_cols: list[str]):
    mask = df[required_cols].isna().any(axis=1)

    failed = df[mask].copy()
    failed["fail_reason"] = "null value"

    return df[~mask].copy(),failed

def check_duplicate_ids(df: pd.DataFrame, id_col: list[str]):
    mask = df.duplicated(subset=id_col, keep=False)

    failed = df[mask].copy()
    failed["fail_reason"] = "duplicate id"

    return df[~mask].copy(), failed

def clean_dates (df: pd.DataFrame,col:str):
    df = df.copy()

    raw = df[col].str.strip().str.strip("\"'")
    df[col] = pd.to_datetime(raw, format=date_format, errors = "coerce")

    mask = df[col].isna() & raw.notna()

    failed = df[mask].copy()
    failed["fail_reason"] = f"invalid date in {col}"

    return df[~mask].copy(), failed
                 
                 

def borrow_length(df:pd.DataFrame, checkout_col: str , return_col: str , new_col: str = "days_borrowed"):
    df = df.copy()
    df[new_col] = (df[return_col]-df[checkout_col]).dt.days.astype("Int64")

    mask = (df[new_col] < 0 ) .fillna(False)

    failed = df[mask].copy()
    failed["fail_reason"] = "negative value"

    return df[~mask].copy(), failed

def export_data(clean: pd.DataFrame, failed: pd.DataFrame, name: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok = True)

    clean.to_csv(out_dir/ f"{name}_cleaned.csv", index=False,date_format= date_format)
    failed.to_csv(out_dir/ f"{name}_failed.csv", index=False,date_format= date_format)

def export_to_sqlite(tables:dict[str, pd.DataFrame], db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        for table_name, df in tables.items():
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"{table_name}: {len(df)} rows written")

def log_counts(run_time: str, table_name: str, rows_in: int, clean: pd.DataFrame, failed:pd.DataFrame):
    rows_passed = len(clean)
    rows_failed = len(failed)

    return{
        "run_time": run_time,
        "table_name": table_name,
        "rows_in": rows_in,
        "rows_passed": rows_passed,
        "rows_failed": rows_failed, 
        "check": "ok" if rows_in == rows_passed + rows_failed else "Mismatch",
    }
#export log fuction
def export_log (log_rows: list[dict],db_path: Path, out_dir: Path):
    log_df = pd.DataFrame(log_rows)
    #db export
    with sqlite3.connect(db_path) as conn:
        log_df.to_sql("pipeline_log", conn, if_exists="append", index=False)

    #csv export
    out_dir.mkdir(parents=True, exist_ok=True)
    log_csv = out_dir / "pipeline_log.csv"
    log_df.to_csv(log_csv,mode="a", header=not log_csv.exists(), index=False)

    print(log_df.to_string(index=False))

#--------------pipeline
def main():
    run_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    df_book = load_data(books_input)
    df_system = load_data(system_input)

    book_rows_in = len(df_book)
    system_rows_in = len(df_system)


    #df_book

    #dates: strip, convert, fail invalid values
    df_book, checkout_failed = clean_dates(df_book, "Book checkout")
    df_book, returned_failed = clean_dates(df_book, "Book Returned")

    # set colum data types
    df_book["Id"] = pd.to_numeric(df_book["Id"], errors = "coerce").astype("Int64")
    df_book["Books"] = df_book["Books"].astype("string")
    df_book["Days allowed to borrow"] = df_book["Days allowed to borrow"].astype("string")
    df_book["Customer ID"] = pd.to_numeric(df_book["Customer ID"], errors = "coerce").astype("Int64")

    #df_system_clean
    # set colum data types
    df_system["Customer ID"] = pd.to_numeric(df_system["Customer ID"], errors = "coerce").astype("Int64")
    df_system["Customer Name"] = df_system["Customer Name"].astype("string")

    #id checks
    df_book, book_null_failed = check_nulls(df_book, book_mask)
    df_book, book_dup_failed = check_duplicate_ids(df_book, pk_cols_Book)

    df_system, system_null_failed = check_nulls(df_system, system_mask)
    df_system, system_dup_failed = check_duplicate_ids(df_system, pk_cols_system)

    

    df_book, borrow_failed = borrow_length(df_book, "Book checkout", "Book Returned")

    

    # combine failures
    book_failed = pd.concat([checkout_failed, returned_failed, book_null_failed ,book_dup_failed , borrow_failed], ignore_index= True)
    book_system = pd.concat([system_null_failed,system_dup_failed ], ignore_index=True)

    export_data(df_book, book_failed, "books", cleaned_path)
    export_data(df_system, book_system, "system", cleaned_path)

    export_to_sqlite({
        "book": df_book,
        "customer": df_system
    },
    db_path,
    )
    # export logs
    export_log([
        log_counts(run_time,"book",book_rows_in,df_book, book_failed),
        log_counts(run_time,"system",system_rows_in,df_system, book_system),
    ],
    db_path,
    cleaned_path
    )

    print("done")
if __name__ == "__main__":
    main()

