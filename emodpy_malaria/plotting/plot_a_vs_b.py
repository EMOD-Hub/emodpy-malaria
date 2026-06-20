import pandas as pd

import emodpy_hiv.plotting.xy_plot as xy_plot


def plot_csv_a_vs_b(a_filename: str,
                    b_filename: str,
                    a_column_prefix: str = "A",
                    b_column_prefix: str = "B",
                    title: str = "A vs B",
                    y_axis_name: str = None,
                    img_dir: str = None):
    """
    Plot the two CSV files against each other.  It is assumed that there is a 'Time'
    column and both files have the same values in that column.
    """
    df_a = pd.read_csv(a_filename)
    df_b = pd.read_csv(b_filename)

    if "Time" not in df_a.columns:
        raise ValueError(f"'Time' column does not exist in the file({a_filename}).")
    if "Time" not in df_b.columns:
        raise ValueError(f"'Time' column does not exist in the file({b_filename}).")

    df_a.index = df_a["Time"]
    df_b.index = df_b["Time"]
    del df_a["Time"]
    del df_b["Time"]

    name_dict = {}
    for column_name in df_a.columns:
        name_dict[column_name] = a_column_prefix + "-" + column_name
    df_a = df_a.rename(columns=name_dict)
    name_dict = {}
    for column_name in df_b.columns:
        name_dict[column_name] = b_column_prefix + "-" + column_name
    df_b = df_b.rename(columns=name_dict)

    xy_plot.xy_plot(img_dir=img_dir,
                    df=df_a,
                    expected_df=df_b,
                    title_1=title,
                    title_2=None,
                    y_axis_name=y_axis_name,
                    fraction_of_total=False,
                    show_legend=True,
                    show_markers=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)
