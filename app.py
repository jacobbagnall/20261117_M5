from pathlib import Path

import pandas as pd

#----------------core variables

#paths
repo_path = Path(__file__).resolve().parent
data_path = repo_path/ "data"
cleaned_path = repo_path/ "clenned"

#input csv
books_input = data_path/ "03_Library Systembook.csv"
system_input = data_path/ "03_Library Systemcustomers.csv"

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

def borrow_length(df:pd.DataFrame, checkout_col: str , return_col: str , new_col: str = "days_borrowed"):
    df = df.copy()
    df[new_col] = (df[return_col]-df[checkout_col]).dt.days.astype("Int64")
    return df

def export_data(clean: pd.DataFrame, failed: pd.DataFrame, name: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok = True)

    clean.to_csv(out_dir/ f"{name}_cleaned.csv", index=False,date_format= date_format)
    failed.to_csv(out_dir/ f"{name}_failed.csv", index=False,date_format= date_format)

#--------------pipeline
def main():
    df_book = load_data(books_input)
    df_system = load_data(system_input)

    #df_book
    # strips ""
    df_book["Book checkout"] = df_book["Book checkout"].str.strip().str.strip("\"'")

    # set colum data types
    df_book["Id"] = pd.to_numeric(df_book["Id"], errors = "coerce").astype("Int64")
    df_book["Books"] = df_book["Books"].astype("string")
    df_book["Book checkout"] = pd.to_datetime(df_book["Book checkout"], format= date_format, errors = "coerce")
    df_book["Book Returned"] = pd.to_datetime(df_book["Book Returned"], format= date_format, errors = "coerce")
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

    df_book = borrow_length(df_book, "Book checkout", "Book Returned")

    # combine failures
    book_failed = pd.concat([book_null_failed,book_dup_failed ], ignore_index=True)
    book_system = pd.concat([system_null_failed,system_dup_failed ], ignore_index=True)

    export_data(df_book, book_failed, "books", cleaned_path)
    export_data(df_system, book_system, "system", cleaned_path)

if __name__ == "__main__":
    main()