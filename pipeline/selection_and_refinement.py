from pathlib import Path
import pandas as pd
from pipeline.hepler_functions import log_success


class SelectionAndRefinement:
    
    @staticmethod
    def get_matching_columns(timetable):
        """
        Determine and return the list of column names required for course schedule matching.

        Args:
            timetable (pandas.DataFrame): The timetable DataFrame whose columns are inspected.

        Returns:
            (list): A list of column names in the correct order

        Raises:
            ValueError:
                - If any required base column is missing.
                - If neither "Tiết" nor "Ca" exists in the DataFrame.
                - If neither "Hệ ĐT" nor "Hệ đào tạo" exists in the DataFrame.
        """

        base_cols = ["Mã MH", "Tên môn", "Nhóm", "Tổ", "Thứ", "Phòng", "Sỉ số", "Giảng viên", "Email cá nhân", "Email TDTU"]        
        missing = set(base_cols) - set(timetable.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        variable_cols = ["Tiết", "Ca"]
        session_col = next((c for c in variable_cols if c in timetable.columns), None)
        if session_col is None:
            raise ValueError("Columns 'Tiết' or 'Ca' were not found in the DataFrame.")
        
        variable_cols = ["Hệ ĐT", "Hệ đào tạo"]
        system_col = next((c for c in variable_cols if c in timetable.columns), None)
        if system_col is None:
            raise ValueError("Columns 'Hệ ĐT' or 'Hệ đào tạo' were not found in the DataFrame.")
        
        # Insert session_col right after "Thứ"
        idx = base_cols.index("Thứ")
        base_cols.insert(idx + 1, session_col)

        return base_cols + [system_col]
    
    
    @staticmethod
    def rename_columns(timetable):
        """
        Standardize column names in the timetable DataFrame.

        Args:
            timetable (pandas.DataFrame): The timetable DataFrame whose columns will be renamed.

        Returns:
            (pandas.DataFrame): A new DataFrame with standardized column names.
        """
        
        col_aliases = {
            "TimeSlot": ["Ca", "Tiết"],
            "Program": ["Hệ ĐT", "Hệ đào tạo"],
        }

        rename_map = {
            "Mã MH": "CourseID",
            "Tên môn": "CourseName",
            "Nhóm": "Group",
            "Tổ": "SubGroup",
            "Thứ": "DayOfWeek",
            "Phòng": "RoomID",
            "Sỉ số": "Capacity",
            "Giảng viên": "Lecturer",
            "Email cá nhân": "PersonalEmail",
            "Email TDTU": "UniversityEmail",
        }

        for standard_col, aliases in col_aliases.items():
            for alias in aliases:
                if alias in timetable.columns:
                    rename_map[alias] = standard_col

        return timetable.rename(columns=rename_map)


    @staticmethod
    def fill_missing_group_code(timetable):
        """
        Fill missing values in the group code column ("Tổ").

        Args:
            timetable (pandas.DataFrame): The timetable DataFrame containing the "Tổ" column.

        Returns:
            (pandas.DataFrame): The DataFrame with missing values in "Tổ" filled with 0.
        """

        timetable["SubGroup"] = timetable["SubGroup"].fillna(0)
        return timetable
    
    
    @staticmethod
    def check_missing(timetable):
        """
        Check a DataFrame for missing values, empty strings, or strings containing only whitespace.
        
        Args:
            timetable (pandas.DataFrame): The DataFrame to check for missing values.
            
        Raises:
            ValueError: If any missing values are detected in the DataFrame.
        """
        
        mask_nan = timetable.isna()
        mask_empty_str = timetable.astype(str).apply(lambda x: x.str.strip() == '')
        mask_missing = mask_nan | mask_empty_str
        
        rows_with_missing = timetable[mask_missing.any(axis=1)]
        
        if len(rows_with_missing) > 0:
            raise ValueError(f"Total number of rows with missing values: {len(rows_with_missing)}")
        else:
            log_success("No missing values found!")


    @staticmethod
    def enforce_column_types(timetable):
        """
        Enforce a standardized data schema for the timetable DataFrame.

        Args:
            timetable (pandas.DataFrame): The input DataFrame after column normalization.

        Returns
            (pandas.DataFrame) The processed DataFrame with enforced column data types.
        """
        
        int_cols = [
            "Group",
            "SubGroup",
            "DayOfWeek",
            "Capacity"
        ]
        
        for col in timetable.columns:
            if col in int_cols:
                timetable[col] = (
                    pd.to_numeric(timetable[col], errors="coerce")  
                    .astype(int)
                )
            else:
                timetable[col] = (
                    timetable[col]
                    .astype(str)
                    .str.strip()
                )
        return timetable

    
    @staticmethod
    def save_files(file_path, data, data_root, out_root):
        """
        Save a pandas DataFrame as a JSON file 
        
        Args:
            file_path (str): Full path to the original data file.
            data (pandas.DataFrame): The processed timetable data to be saved.
            data_root (str): Root directory of the input dataset.
            out_root (str): Root directory where the output JSON files will be stored.
        """
        
        relative_path = file_path.relative_to(data_root).parent
        save_dir = Path(out_root) / relative_path
        save_dir.mkdir(parents=True, exist_ok=True)

        json_path = save_dir / "timetable.json"

        data.to_json(
            json_path,
            orient="records",    
            force_ascii=False,    
            indent=4
        )
        log_success(f"Saved: {json_path}")