import pandas as pd
import os
import matplotlib.pyplot as plt


def create_common_x_values(a_old, b_old):
    """
    Matplotlib needs the x-values to be the same for different (x,y) lines being plotted.
    This method creates a new version of each set of values.
    """
    a_new = []
    b_new = []

    a_index = 0
    b_index = 0
    while (a_index < len(a_old)) and (b_index < len(b_old)):
        a = a_old[a_index]
        b = b_old[b_index]
        if a < b:
            if b_index == 0:
                a_new.append(a_old[a_index])
                a_index = a_index + 1
            else:
                a_new.append(a_old[a_index])
                b_new.append(a_old[a_index])
                a_index = a_index + 1
        elif a == b:
            a_new.append(a_old[a_index])
            b_new.append(b_old[b_index])
            a_index = a_index + 1
            b_index = b_index + 1
        else:
            if a_index == 0:
                b_new.append(b_old[b_index])
                b_index = b_index + 1
            else:
                a_new.append(b_old[b_index])
                b_new.append(b_old[b_index])
                b_index = b_index + 1

    while a_index < len(a_old):
        a_new.append(a_old[a_index])
        a_index = a_index + 1

    while b_index < len(b_old):
        b_new.append(b_old[b_index])
        b_index = b_index + 1

    return a_new, b_new


def fill_in_y_values(x_old, y_old, x_new):
    """
    Since matplotlib needs the lines/curves to have the same X-values,
    we need to find the associated Y-values when we add the new X-values.
    This method uses linear interpolation to find the values between points.
    """
    y_new = []

    x_old_index = 0
    x_new_index = 0
    while (x_old_index < len(x_old)) and (x_new_index < len(x_new)):
        if x_old[x_old_index] == x_new[x_new_index]:
            y_new.append(y_old[x_old_index])
            x_old_index = x_old_index + 1
            x_new_index = x_new_index + 1
        elif x_old[x_old_index] > x_new[x_new_index]:
            x1 = x_old[x_old_index - 1]  # noqa: E201, E202
            x2 = x_old[x_old_index    ]  # noqa: E201, E202
            y1 = y_old[x_old_index - 1]  # noqa: E201, E202
            y2 = y_old[x_old_index    ]  # noqa: E201, E202
            x  = x_new[x_new_index    ]  # noqa: E201, E202, E221
            y  = y1 + (x - x1) * (y2 - y1) / (x2 - x1)   # noqa: E221
            y_new.append(y)
            x_new_index = x_new_index + 1
        else:
            raise ValueError("shouldn't get here")

    return y_new


def get_color_name(idx: int):
    color_names = ['red', 'blue', 'limegreen', 'cyan', 'magenta', 'orange', 'black']
    return color_names[idx % len(color_names)]


def get_line_style(idx: int):
    ls_list = ["-", "--", ":", "-."]
    return ls_list[idx % len(ls_list)]


def get_marker_style(idx: int):
    marker_list = ["o", "v", "*", "^", "s", "P"]
    return marker_list[idx % len(marker_list)]


def xy_plot(img_dir: str,
            df: pd.DataFrame,
            title_1: str,
            title_2: str,
            x_axis_name: str = "Years",
            y_axis_name: str = "",
            expected_df: pd.DataFrame = None,
            fraction_of_total: bool = False,
            show_legend: bool = True,
            show_markers: bool = True,
            min_x: float = None,
            max_x: float = None,
            min_y: float = None,
            max_y: float = None,
            x_axis_as_log_scale: bool = False,
            y_axis_as_log_scale: bool = False):
    """
    Create a plot using the give dataframe, 'df', with all of the appropriate labels.
    The index of the dataframe will be used for the X-axis and the lines or curves will
    be for each column of the dataframe.

    Args:
        img_dir (str, required):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

        df (DataFrame, required):
            A dataframe where the index will be used for the X-values and each column will get
            a separate line/curve.  The name of the column will be used in the legend.

        title_1 (str, required):
            This will be the top line text on the plot.

        title_2 (str, required):
            This will be the second line of text ohe plot.

        x_axis_name (str, optional):
            This is the label used to indicate what the X-axis values are.

        y_axis_name (str, optional):
            This is the label used to indicate what the Y-axis values are.

        expected_df (DataFame, optional):
            This dataframe is expected to have a similar format to the 'df' dataframe.
            The index of the dataframe is the X-values and should similar to that of 'df'.
            The columns are the Y-values and each column creates a separate line/curve.
            However, these will be plotted in black, the markers a little larger, and
            on top of the lines from the 'df'.

        fraction_of_total (bool, optional):
            If true, the columns of each dataframe are summed and divided by this sum
            to create a fraction of the total.

        show_legend (bool, optional):
            If True a legend will be placed on the right side of the plot, but beware
            that long column names can make the plot space very small.

        show_markers (bool, optional):
            if True the lines will have markers at each data point.

        min_x (float, optional):
            If provided the plot will have a fixed minimum value for the X-axis
            independent of the data.  When not provided, matplotlib determines
            the minimum based on the data.

        max_x (float, optional):
            If provided the plot will have a fixed maximum value for the X-axis
            independent of the data.  When not provided, matplotlib determines
            the minimum based on the data.

        min_y (float, optional):
            If provided the plot will have a fixed minimum value for the Y-axis
            independent of the data.  When not provided, matplotlib determines
            the minimum based on the data.

        max_y (float, optional):
            If provided the plot will have a fixed maximum value for the Y-axis
            independent of the data.  When not provided, matplotlib determines
            the minimum based on the data.

        x_axis_as_log_scale (bool, optional):
            If True, the X-axis is assumed to be logrithmic.

        y_axis_as_log_scale (bool, optional):
            If True, the Y-axis is assumed to be logrithmic.

    Returns:
    """

    fig, ax = plt.subplots(layout='constrained')

    if fraction_of_total:
        column_names = df.columns
        df["total"] = 0
        for col_name in column_names:
            df["total"] = df["total"] + df[col_name]
        for col_name in column_names:
            df[col_name] = df[col_name] / df["total"]
        del df["total"]

    x_act_new = df.index.values.tolist()

    color_index = 0
    marker_index = 0
    ls_index = 0

    if expected_df is not None:
        x_exp_old = expected_df.index.values.tolist()
        x_act_old = df.index.values.tolist()
        x_exp_new, x_act_new = create_common_x_values(x_exp_old, x_act_old)

    column_names = df.columns.tolist()
    x_act_old = df.index.values.tolist()

    color_index = 0
    marker_index = 0
    ls_index = 0

    for col_name in column_names:
        y_act_old = df[col_name].values.tolist()

        y_act_new = fill_in_y_values(x_act_old, y_act_old, x_act_new)

        clr = get_color_name(color_index)
        ls  = get_line_style(ls_index)       # noqa: E221
        ms  = get_marker_style(marker_index) # noqa: E221

        if show_markers:
            ax.plot(x_act_new, y_act_new, c=clr, marker=ms, markersize=4, linewidth=1.0, linestyle=ls, label=col_name)
        else:
            ax.plot(x_act_new, y_act_new, c=clr, linewidth=1.0, linestyle=ls, label=col_name)

        marker_index = marker_index + 1
        color_index  = color_index  + 1  # noqa: E221
        ls_index     = ls_index     + 1  # noqa: E221

    if expected_df is not None:
        column_names = expected_df.columns.tolist()

        color_index = 0
        marker_index = 0
        ls_index = 0

        for col_name in column_names:
            y_exp_old = expected_df[col_name].values.tolist()

            y_exp_new = fill_in_y_values(x_exp_old, y_exp_old, x_exp_new)

            clr = get_color_name(6) # 6 = black
            ls  = get_line_style(ls_index)       # noqa: E221
            ms  = get_marker_style(marker_index) # noqa: E221

            if show_markers:
                ax.plot(x_exp_new, y_exp_new, c=clr, marker=ms, markersize=6, linewidth=2.0, linestyle=ls, label=col_name)
            else:
                ax.plot(x_exp_new, y_exp_new, c=clr, linewidth=2.0, linestyle=ls, label=col_name)

            marker_index = marker_index + 1
            ls_index = ls_index + 1
            color_index = color_index + 1

    if x_axis_as_log_scale:
        ax.set_xscale('log')
    elif max_x is not None:
        max = max_x
        min = 0.0
        if min_x is not None:
            min = min_x
        ax.set_xlim([min, max])

    if y_axis_as_log_scale:
        ax.set_yscale('log')
    elif max_y is not None:
        max = max_y
        min = 0.0
        if min_y is not None:
            min = min_y
        ax.set_ylim([min, max])

    ax.minorticks_on()
    ax.grid(which="major", color='darkgray', linewidth=0.5, linestyle='--')
    ax.grid(which="minor", color='gray'    , linewidth=0.1, linestyle='--') # noqa: E203

    if show_legend:
        ax.legend(loc="upper left", bbox_to_anchor=(1.0, 0.75), fontsize='8')

    ax.set_xlabel(x_axis_name)
    ax.set_ylabel(y_axis_name)
    if isinstance(x_act_new[0], str):
        x_act_new = df.index.values.tolist()
        plt.xticks(range(len(x_act_new)), x_act_new, rotation=45, ha='right')
    title = title_1
    if title_2 is not None:
        title = title + "\n" + title_2
    fig.suptitle(title, fontsize='14')

    if img_dir:
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        title_1 = title_1.replace(" ", "_")
        fn = os.path.join(img_dir, title_1 + ".png")
        print(fn)
        fig.set_size_inches(9, 6)
        fig.savefig(fn, dpi=300)
    else:
        plt.show()
    plt.close(fig)

    return
