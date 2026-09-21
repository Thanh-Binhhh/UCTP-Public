import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pipeline.helper_functions import print_df


class Visualization:
    
    @staticmethod
    def chart(ax, semester, before, after, title):
        """
        Plot a bar chart comparing row counts before and after data cleaning.

        Args:
            ax (matplotlib.axes.Axes): The Matplotlib Axes object on which the chart will be drawn.
            semester (list or array-like): Labels for the x-axis.
            before (list or array-like): Row counts before data cleaning.
            after (list or array-like): Row counts after data cleaning.
            title (str): Title of the chart.
        """
        
        width = 0.7
        bars_before = ax.bar(semester, before, width, color='#EDC5C8', label='Before')
        bars_after = ax.bar(semester, after, width, color='#A3D78A', label='After')

        for bar in bars_before:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                f"{int(height)}",
                ha='center', va='bottom',
                fontsize=10
            )

        for bar in bars_after:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                f"{int(height)}",
                ha='center', va='bottom',
                fontsize=10
            )

        ax.set_xlabel("Semester")
        ax.set_ylabel("Row Counts")
        ax.set_title(title, fontsize=14)
        ax.legend()
   
    
    @staticmethod
    def display_chart_for_overall_summary(df_summary):
        """
        Display an overall bar chart summarizing total and remaining records by semester.

        Args:
            df_summary (pandas.DataFrame): Summary DataFrame containing the following required columns:
                'Academic year': Academic year label.
                'Semester': Semester label.
                'Total rows': Total number of records before processing.
                'Remaining rows': Number of records remaining after processing.
        """
        
        semester = df_summary["Academic year"] + "/" + df_summary["Semester"]
        before = df_summary["Total rows"]
        after = df_summary["Remaining rows"]

        _, ax = plt.subplots(figsize=(14, 6))
        Visualization.chart(
            ax,
            semester,
            before,
            after,
            "TOTAL EXCLUDED RECORDS BEFORE AND AFTER PROCESSING BY SEMESTER"
        )
        plt.tight_layout()
        plt.show()

        
    @staticmethod
    def display_chart_for_each_stages(record_statistics):
        """
        Display bar charts comparing record counts at different processing stages.

        Args:
            record_statistics (pandas.DataFrame): Summary DataFrame containing record count statistics.
                - 'Academic year'
                - 'Semester'
                - 'Total rows'
                - 'Remaining rows'
        """
        
        df = record_statistics.head(4)
        semester = df["Academic year"] + "/" + df["Semester"]
        before = df["Total rows"]
        after = df["Remaining rows"]
        
        _, axes = plt.subplots(1, 2, figsize=(20, 6))

        # Plot for data preprocessing stage
        Visualization.chart(
            axes[0],
            semester,
            before,
            after,
            "RECORDS COUNTS BEFORE AND AFTER DATA PREPROCESSING BY SEMESTER"
        )
        
        # Plot for data inconsistency stage
        df = record_statistics.tail(4)
        before = df["Total rows"]
        after = df["Remaining rows"]

        Visualization.chart(
            axes[1],
            semester,
            before,
            after,
            "RECORDS COUNTS BEFORE AND AFTER DATA INCONSISTENCY BY SEMESTER"
        )
        plt.tight_layout()
        plt.show()

        
    @staticmethod
    def count_total_excluded_data(record_statistics):
        """
        Aggregate and calculate total excluded records by academic year and semester.

        Args:
            record_statistics (pandas.DataFrame):  A summary statistics DataFrame containing the following required columns:
                - 'Academic year': Academic year of the semester.
                - 'Semester': Semester identifier.
                - 'Total rows': Total number of records before processing.
                - 'Excluded rows': Number of records excluded at each processing stage.

        Returns:
            (pandas.DataFrame): A DataFrame with one row per academic year and semester, including:
                - 'Academic year'
                - 'Semester'
                - 'Total rows'
                - 'Excluded rows'
                - 'Remaining rows'
                - 'Percentage of excluded data'
        """
        
        columns = ["Academic year", "Semester", "Total rows", "Excluded rows", "Remaining rows", "Percentage of excluded data"]
        result = pd.DataFrame(columns=columns)
        record_statistics = record_statistics.groupby(["Academic year","Semester"])
        
        for (year, semester), group in record_statistics:
            total_rows = group["Total rows"].iloc[0]
            excluded_rows = group["Excluded rows"].iloc[0] + group["Excluded rows"].iloc[1]
            percentage = (excluded_rows / total_rows) * 100
            
            new_rows = pd.DataFrame([
                {
                    "Academic year": year, 
                    "Semester": semester, 
                    "Total rows": total_rows, 
                    "Excluded rows": excluded_rows, 
                    "Remaining rows": total_rows - excluded_rows, 
                    "Percentage of excluded data": percentage
                }
            ])

            if not new_rows.empty:
                result = pd.concat([result, new_rows], ignore_index=True)
        return result
        
       
    @staticmethod
    def count_excluded_data(record_statistics):      
        """
        Calculate excluded record statistics for each processing stage by semester.

        Args:
            record_statistics (pandas.DataFrame): A summary statistics DataFrame containing the following required columns:
                - 'Academic year'
                - 'Semester'
                - 'Total rows'
                - 'Excluded rows'
                - 'Remaining rows'

        Returns:
            list[pandas.DataFrame]: A list of DataFrames, one per academic year and semester.
                Each DataFrame contains the following columns:
                - 'Stage'
                - 'Excluded rows'
                - 'Remaining rows'
                - 'Percentage of excluded data'
        """
        
        columns = ["Stage", "Excluded rows", "Remaining rows", "Percentage of excluded data"]
        result = []
        record_statistics = record_statistics.groupby(["Academic year","Semester"])
        
        for _, group in record_statistics:                  
            df = pd.DataFrame(columns=columns)    
            total_rows = group["Total rows"].iloc[0]
            excluded_rows = group["Excluded rows"].iloc[0] + group["Excluded rows"].iloc[1]
            percentage = (excluded_rows / total_rows) * 100       
            
            new_rows = pd.DataFrame([
                {
                    "Stage": "Rows excluded due to data preprocessing", 
                    "Excluded rows": group["Excluded rows"].iloc[0], 
                    "Remaining rows": group["Remaining rows"].iloc[0], 
                    "Percentage of excluded data": (group["Excluded rows"].iloc[0] / group["Total rows"].iloc[0]) * 100, 
                },
                {
                    "Stage": "Rows excluded due to data inconsistency", 
                    "Excluded rows": group["Excluded rows"].iloc[1], 
                    "Remaining rows": group["Remaining rows"].iloc[1], 
                    "Percentage of excluded data": (group["Excluded rows"].iloc[1] / group["Total rows"].iloc[0]) * 100, 
                },
                {
                    "Stage": "Total", 
                    "Excluded rows": excluded_rows, 
                    "Remaining rows": np.nan, 
                    "Percentage of excluded data": percentage, 
                }
            ])
            
            if not new_rows.empty:
                df = pd.concat([df, new_rows], ignore_index=True)
                result.append(df)
        return result