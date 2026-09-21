from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from IPython.display import display
from openpyxl.styles import PatternFill
from pandas.core.groupby.generic import DataFrameGroupBy


def normalize_statistics_df(df):
    """
    Reformat and clean specific columns in a statistics DataFrame.
    1. Removes any text enclosed in parentheses '()' from the 'Course Name' column, if present.
    2. Converts non-null values in the 'Remaining rows' column to integers.
    3. Formats percentage-related columns to strings with one decimal place and a '%' sign.

    Args:
        df (pandas.DataFrame): Input DataFrame.

    Returns:
        (pandas.DataFrame): The updated DataFrame with reformatted and cleaned values.
    """
    
    # Remove parentheses in "Course name"
    if "Course name" in df.columns:
        df["Course name"] = (
            df["Course name"]
            .astype(str)
            .str.replace(r"\s*\(.*?\)", "", regex=True)
        )
    
    # Convert values in "Remaining rows" to integer
    if "Remaining rows" in df.columns:
        df["Remaining rows"] = df["Remaining rows"].astype("Int64")

    # Format percentage columns
    cols = [
        "Percentage before",
        "Percentage after",
        "Difference",
        "Percentage of excluded data"
    ]

    for col in cols:
        if col in df.columns:
            df[col] = df[col].map(
                lambda x: f"{x:.1f}%" if pd.notna(x) else x
            )
    return df


def log_success(msg):
    """
    Print a success message in green text in the terminal.

    Args:
        msg (str): The success message to display.
    """
    print(f"\033[32m {msg}\033[0m.")


def log_error(msg):
    """
    Print an error message in red text in the terminal.

    Args:
        msg (str): The error message to display.
    """
    print(f"\033[31m {msg}\033[0m.")
    

def print_df(df):
    """
    Display a styled pandas DataFrame with formatting.

    Args:
        df (pd.DataFrame): The DataFrame to display.
    """
    
    style = (
        df.style
        .set_properties(**{
            'border': '1px solid gray',
            'padding': '5px',
            'font-size': '12px'
        })
        .set_table_styles([
            {"selector": "th", "props": [("background-color", "#f2f2f2"), ("font-weight", "bold")]}
        ])
    )
    display(style)
    

def highlight_row(df):
    """
    Highlight rows in a DataFrame that match a specific condition.

    Parameters:
        df (pandas.DataFrame): The DataFrame to apply highlighting to.

    Returns:
        (pandas.io.formats.style.Styler): A Styler object with background color applied to matching rows.
    """
    
    def _highlight(row):
        value = float(row["Difference"].rstrip('%'))
        if value != 0:
            return ['background-color: #F2DCDB'] * len(row)
        return [''] * len(row)
    
    return df.style.apply(_highlight, axis=1)
    
    
def highlight_excel(path, row_indices, color="F2DCDB"):
    """
    Highlight specific rows in an Excel file based on their indices.

    Args:
        path (str): Path to the Excel file to modify.
        row_indices (list[int]): List of 1-based row indices to highlight.
        color (str, optional): HEX color code used to fill the background.
    """

    wb = load_workbook(path)
    ws = wb.active
    fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

    for i in row_indices:
        if i <= ws.max_row:
            for cell in ws[i]:
                cell.fill = fill
    wb.save(path)
    

def save_files(file_path, data, data_root, out_root, file_type: str = "parquet"):
    """
    Save a pandas DataFrame or DataFrameGroupBy output to files in the output folder.
    
    Args:
        file_path (str | Path): Full path to the original data file.
        data (pandas.DataFrame): The DataFrame to save.
        data_root (str): The root folder of the input data.
        out_root (str): The root folder for output files.
        file_type (str): Output file type: 'parquet' or 'excel'.
    """
    
    file_type = file_type.lower()
    if file_type not in {"parquet", "xlsx"}:
        raise ValueError("file_type must be one of: parquet or xlsx")

    file_path = Path(file_path)
    data_root = Path(data_root)
    out_root = Path(out_root)

    # Create the corresponding path in output/ 
    rel_path = file_path.relative_to(data_root)
    save_path = (out_root / rel_path).with_suffix(f".{file_type}")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _save(df: pd.DataFrame, path: Path):
        if file_type == "parquet":
            df.to_parquet(path, index=False)
        else:
            df.to_excel(path, index=False)

    if isinstance(data, pd.DataFrame):
        _save(data, save_path)

    elif isinstance(data, list) and all(
            isinstance(x, tuple) and isinstance(x[1], pd.DataFrame)
            for x in data
        ):
        for i, (_, group_df) in enumerate(data, start=1):
            group_path = save_path.with_name(f"{save_path.stem}_{i}.{file_type}")
            _save(group_df, group_path)

    log_success(f"Saved: {save_path}")