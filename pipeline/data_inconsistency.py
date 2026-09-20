from .hepler_functions import log_success, highlight_excel
import pandas as pd


class Inconsistency:    
    
    @staticmethod
    def get_matching_columns(df):
        """
        Return the appropriate list of column names for course schedule matching.

        Args:
            df (pandas.DataFrame): The DataFrame from which to detect the time-column name.

        Returns
            (list): A list of column names including both required columns and the detected time-column ("Tiết" or "Ca").

        Raises
            (ValueError): If neither "Tiết" nor "Ca" exists in the DataFrame.
        """

        base_cols = ["Mã MH", "Nhóm", "Tổ", "Thứ", "Tuần học", "Phòng", "Giảng viên"]
        variable_cols = ["Tiết", "Ca"]

        actual_col = next((c for c in variable_cols if c in df.columns), None)

        if actual_col is None:
            raise ValueError("Columns 'Tiết' or 'Ca' were not found in the DataFrame.")
        return base_cols + [actual_col]
    
    
    @staticmethod
    def check_for_duplication(data, columns):
        """
        Check for duplicate rows in a DataFrame based on specific columns.

        Args:
            data (pd.DataFrame): Input DataFrame containing schedule data.
            columns (list): Columns to check for duplication.
        """

        data.index = range(2, 2 + len(data))
        data["duplicate_data"] = data.duplicated(subset=columns, keep=False)
        df_duplicates = data[data["duplicate_data"]]

        if df_duplicates.empty:
            return None
        return df_duplicates.groupby(columns)
    
    
    @staticmethod
    def mark_duplicates(grouped_duplicate_indexes, path):
        """
        Highlight and display duplicate rows from grouped duplicate data.

        Args:
            grouped_duplicate_indexes (pandas.DataFrameGroupBy): The grouped duplicate rows.
            path (str): The path of the file used for highlighting.
        """
        
        duplicate_indexes = set()
        
        for _, value in grouped_duplicate_indexes:
            duplicate_indexes.update(value.index.tolist())

        if duplicate_indexes:
            # flatten_index_duplicate = list(set(sum(index_duplicate, ())))
            highlight_excel(path, sorted(duplicate_indexes))
            log_success(f"Highlighted {len(duplicate_indexes)} duplicate rows in {path}.")
    
    
    # ==========================================
    # Data summary statistics
    # ==========================================
    
    @staticmethod
    def prepare_statistics(timetable):
        """
        Initialize statistics for courses and education systems.
        
        Args:
            timetable (pandas.DataFrame): The timetable data.

        Returns: 
            (tuple): A tuple containing:
                courses_statistics (pandas.DataFrame): Statistics for each course.
                systems_statistics (pandas.DataFrame): Statistics for each education system.
        """    
        
        # --- Course stats ---
        courses = timetable["Mã MH"].drop_duplicates()
        
        courses_stats = [
            [
                timetable.loc[timetable["Mã MH"] == course_code, "Tên môn"].iloc[0],    # Course name corresponding to course_code
                course_code,                                    
                (timetable["Mã MH"] == course_code).sum(),                              # Pre-cleaning class count
                100.0,                                                                  # Pre-cleaning class percentage
                (timetable["Mã MH"] == course_code).sum(),                              # After-cleaning class count
                100.0,                                                                  # After-cleaning class percentage
                0.0                                                                     # Difference between before and after
            ]
            for course_code in courses.values
        ]
        
        courses_statistics = pd.DataFrame(courses_stats, 
                                columns=["Course name", "Course ID", "Classes before cleaning", "Percentage before", "Classes after cleaning", "Percentage after", "Difference"])
        
        
        # --- System stats ---
        systems = timetable["Hệ ĐT"].unique()

        systems_stats = [
            [
                system,
                (timetable["Hệ ĐT"] == system).sum(),
                100.0,
                (timetable["Hệ ĐT"] == system).sum(),
                100.0,
                0.0
            ]
            for system in systems
        ]
        systems_statistics = pd.DataFrame(systems_stats, 
                                columns=["Education system","Classes before cleaning", "Percentage before","Classes after cleaning","Percentage after","Difference"])
        return courses_statistics, systems_statistics
    
    
    @staticmethod
    def update_statistics(timetable, courses_statistics, systems_statistics):
        """
        Compute statistics for courses and education systems.
        
        Args:
            timetable (pandas.DataFrame): The timetable data.
            courses_statistics (pandas.DataFrame): Statistics for each course.
            systems_statistics (pandas.DataFrame): Statistics for each education system.

        Returns: 
            (tuple): A tuple containing:
                courses_statistics (pandas.DataFrame): Statistics for each course.
                systems_statistics (pandas.DataFrame): Statistics for each education system.
        """    
        
        # --- Course stats ---
        for idx, row in courses_statistics.iterrows():
            course_code = row["Course ID"]
            count_before = row["Classes before cleaning"]
            count_after = (timetable["Mã MH"] == course_code).sum()

            if count_before == count_after:
                continue

            percent_after = round((count_after / count_before) * 100, 3)
            diff = round(100 - percent_after, 3)

            courses_statistics.loc[idx, [
                "Classes after cleaning",
                "Percentage after",
                "Difference"
            ]] = [count_after, percent_after, diff]
        
        # --- System stats ---
        for idx, row in systems_statistics.iterrows():
            system = row["Education system"]
            count_before = row["Classes before cleaning"]
            count_after = (timetable["Hệ ĐT"] == system).sum()
            
            if count_before == count_after:
                continue

            percent_after = round((count_after / count_before) * 100, 3)
            diff = round(100 - percent_after, 3)

            systems_statistics.loc[idx, [
                "Classes after cleaning",
                "Percentage after",
                "Difference"
            ]] = [count_after, percent_after, diff]
        
        return courses_statistics, systems_statistics
    
    
    @staticmethod
    def get_difference_statistics(testing_timetable, statistics, rows, config):
        """
        Calculate the percentage difference in class counts after data cleaning.

        Args:
            testing_timetable (pandas.DataFrame): The cleaned timetable DataFrame used for comparison.
            statistics (pandas.DataFrame): The original statistics DataFrame containing class counts.
            rows (pandas.DataFrame): Rows representing classes that are not included in the cleaned testing timetable.
            config (dict): Configuration dictionary that specifies column names: 'col_in_statistics' or 'col_in_timetable'

        Returns:
            float or list[float]: 
                A single percentage difference if only one unique class is missing from the timetable.
                or, A list of percentage differences if multiple classes are missing.
        """

        def _get_difference_statistics(key):
            mask = statistics[config["col_in_statistics"]] == key
            count_before = statistics.loc[mask, "Classes before cleaning"].values[0]
            count_after = (testing_timetable[config["col_in_timetable"]] == key).sum()
            percent_after = round((count_after / count_before) * 100, 3)
            return round(100 - percent_after, 3)
        
        # "Mã MH" or "Hệ ĐT"
        keys = rows[config["col_in_timetable"]].unique()

        # If only one class is not included in the testing timetable.
        if len(keys) == 1:
            diff = _get_difference_statistics(keys[0])
            
        # If multiple classes are not included in the testing timetable.
        else:
            diff = []
            for key, _ in rows.groupby(config["col_in_timetable"]):
                diff.append(_get_difference_statistics(key))
                
        return diff
    
    
    # ==========================================
    # Data conflict handling
    # ==========================================

    @staticmethod
    def find_row(df, row):
        """
        Find row in a DataFrame that exactly match the given Series on specific columns.

        Args:
            df (pd.DataFrame): The DataFrame to search.
            row (pd.Series): The row to match against, with values for specific columns.

        Returns:
            pd.Series: A boolean mask indicating which rows in df match the given row.

        Raises:
            ValueError: If no matching row is found.
        """
        
        cols = Inconsistency.get_matching_columns(df)
        
        row_aligned = row.reindex(cols)
        row_df = pd.DataFrame([row_aligned])
        merged = df.merge(row_df, on=cols, how="inner")
        
        if merged.empty:
            raise ValueError("There are no matching rows")
        
        return merged
    
    
    def is_single_class(df):
        """
        Check whether the given DataFrame represents a single class.

        A class is defined by having only one unique value for each of the 
        following columns "Mã MH", "Nhóm", "Tổ"     

        Args:
            df (pandas.DataFrame) DataFrame containing at least the columns "Mã MH", "Nhóm", and "Tổ".

        Returns
            (bool) True if all three columns each contain exactly one unique value.
                False otherwise.
        """
        
        cols = ["Mã MH", "Nhóm", "Tổ"]
        check = df[cols].nunique()
        return (check == 1).all()
    
    
    @staticmethod
    def remove_rows(timetable, rows):
        """
        Remove rows from a timetable DataFrame that exactly match the given rows on specific columns.

        Args:
            timetable (pd.DataFrame): The original timetable DataFrame.
            rows (pd.DataFrame): DataFrame containing rows to remove.

        Returns:
            pd.DataFrame: A copy of timetable with matching rows removed.

        Raises:
            ValueError: If no matching rows are found to remove.
        """
        
        cols = Inconsistency.get_matching_columns(timetable)
        
        mask = timetable[cols].apply(tuple, axis=1).isin(rows[cols].drop_duplicates().apply(tuple, axis=1))
        
        if mask.empty:
            raise ValueError("There are no matching rows to remove")

        log_success(f"Deleted {mask.sum()} row(s)")
        return timetable[~mask]   
    
    
    @staticmethod
    def update_timetable(timetable, group, tmp_courses_statistics, tmp_systems_statistics):
        """
        Decide which row to remove from a DataFrame of duplicate timetable entries 
        based on course and system differences, then remove it from the original timetable.
        
        Args:
            timetable (pandas.DataFrame): The timetable DataFrame to be updated.
            group (pandas.DataFrame): A DataFrame containing duplicate rows to analyze.
            tmp_courses_statistics (list of tuples): List of tuples `(index, value)` representing the difference metric 
                                            for each duplicate row based on courses.
            tmp_systems_statistics (list of tuples): List of tuples `(index, value)` representing the difference metric 
                                            for each duplicate row based on education systems.                     

        Returns:
            pandas.DataFrame: Updated timetable DataFrame with one duplicate row removed.
        """
        
        def normalize(v):
            return sum(v) if isinstance(v, list) else v
        
        # First, find the minimum values in both statistics.
        min_course_val = min(normalize(v) for _, v in tmp_courses_statistics)
        min_system_val = min(normalize(v) for _, v in tmp_systems_statistics)
        
        # Identify the classes with the smallest differences in tmp_courses_statistics and tmp_systems_statistics, 
        # and select the class that satisfies both conditions.
        candidate_course = {i for i, v in tmp_courses_statistics if normalize(v) == min_course_val}
        candidate_system = {i for i, v in tmp_systems_statistics if normalize(v) == min_system_val}
        common_indices = candidate_course & candidate_system
        
        # If there are common indices
        if common_indices:
            idx_to_keep = min(common_indices)
            
        # Ortherwise, calculate the total differences and remove rows with the smallest total difference.
        else:
            all_indices = (
                {idx for idx, _ in tmp_courses_statistics}
                | {idx for idx, _ in tmp_systems_statistics}
            )

            def total_diff(idx):
                course = next((normalize(v) for i, v in tmp_courses_statistics if i == idx), 0)
                system = next((normalize(v) for i, v in tmp_systems_statistics if i == idx), 0)
                return course + system

            idx_to_keep = min(all_indices, key=total_diff)

        timetable = Inconsistency.remove_rows(timetable, group.drop(idx_to_keep))
        return timetable