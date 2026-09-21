import re
from .helper_functions import log_success, log_error


class Preprocessing:
    
    @staticmethod
    def find_final_sheet(file_path):
        """
        Read the sheet whose name contains the word 'final' from an Excel file.

        Args:
            file_path (str): Path to the Excel file.

        Returns:
            str: The name of the first sheet that contains 'final'.

        Raises:
            ValueError: If no sheet containing 'final' is found in the file.
        """
        
        final_sheets = [s for s in file_path.sheet_names if "final" in s.lower()]

        if not final_sheets:
            raise ValueError(f"No sheet containing 'final' found in file: {file_path}")
        return final_sheets[0]
    
    
    @staticmethod
    def normalize_string_columns(data, cols):
        """
        Normalize specified columns by converting them to pandas StringDtype.

        Args:
            data (pandas.DataFrame): The input DataFrame to process.
            cols (list[str]): A list of column names to be converted to string type.

        Returns:
            (pandas.DataFrame): The DataFrame with the specified columns converted to pandas StringDtype.
        """

        data[cols] = data[cols].astype("string")
        return data
    
    
    @staticmethod
    def count_invalid_emails(timetable, cols):
        """
        Validate email columns in a pandas DataFrame.

        This function checks each specified email column for:
        1. Empty values 
        2. Invalid email formats based on a practical regex pattern

        Args
            timetable (pandas.DataFrame) The DataFrame containing timetable data read from Excel.
            cols (list[str]): A list of column names that contain email addresses
        """
        
        email_pattern = re.compile(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )

        for col in cols:
            series = (
                timetable[col]
                .fillna("")         
                .astype(str)        
                .str.strip()
            )

            empty_count = (series == "").sum()

            invalid_count = (
                (series != "") &
                (~series.str.match(email_pattern))
            ).sum()

            if empty_count == 0 and invalid_count == 0:
                log_success(f"{col}: All emails valid")
            else:
                log_error(f"{col}: {invalid_count} invalid emails")

    
    # ==========================================
    # Exclusion of redundant data
    # ==========================================

    @staticmethod
    def remove_rows(data, column, keyword):
        """
        Remove rows containing a specific keyword from a DataFrame and highlight them in Excel.

        Args:
            data (pandas.DataFrame): The input DataFrame to process.
            column (str): The column name to check for the keyword.
            keyword (str | int): The keyword used to identify rows that should be removed.

        Raises:
            ValueError: If the keyword type is invalid.
        """

        before = len(data)
        keep_mask = ~data[column].str.contains(keyword, case=False, na=False, regex=False)
        data = data.loc[keep_mask].copy()
        after = len(data)

        log_success(f"Removed {before - after} rows containing '{keyword}' in column '{column}'")
        return data
    
    
    @staticmethod
    def remove_rows_by_numeric_condition(data, column):
        """
        Remove rows where the class size is 0.

        Args:
            data (pd.DataFrame): The input DataFrame to process.
            column (str): The name of the column to apply the numeric condition on.
            
        Raises:
            ValueError: If the specified column does not exist in the DataFrame
                        or the condition string is invalid.
        """

        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame.")

        before = len(data)
        mask = (data[column] == 0) | (data[column].isna()) | (data[column].astype(str).str.strip() == '')
        data = data.loc[~mask]
        after = len(data)

        log_success(f"Removed {before - after} rows with value 0 in column '{column}'")
        return data