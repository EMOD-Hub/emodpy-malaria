import sys
import argparse
import pandas as pd
import json

import emodpy_hiv.plotting.helpers as helpers
import emodpy_hiv.plotting.plot_inset_chart as pic
from emodpy_hiv.plotting.channel_report import ChannelReport


def calculate_mean(dir_name: str):
    """
    Calculate the mean of the InsetChart.json files in the given directory.

    Args:
        dir_name:
            Directory with InsetChart.json files

    Return:
        mean_cr: Mean ChannelReport object
        raw_data_list: List of raw data dictionaries from the InsetChart.json files
    """
    test_filenames = helpers.get_filenames(dir_or_filename=dir_name,
                                           file_prefix="InsetChart",
                                           file_extension="json")

    raw_data_list = []
    total_df = pd.DataFrame()
    for test_fn in test_filenames:
        with open(test_fn, "r") as test_file:
            test_json = json.loads(test_file.read())
            raw_data_list.append(test_json)
        df = ChannelReport.convert_to_df(test_json)
        total_df = pd.concat([total_df, df])

    mean_df = total_df.groupby("Time").mean().reset_index()
    mean_cr = ChannelReport(df=mean_df)
    mean_cr = mean_cr.convert_df_to_channel_report(df=mean_df)

    return mean_cr, raw_data_list


def plot_mean(dir1: str,
              dir2: str,
              dir3: str,
              title: str = None,
              show_raw_data: bool = False,
              subplot_index_min: int = 0,
              subplot_index_max: int = 100,
              output: str = None):
    """
    Plot the mean of the InsetChart.json files in the given directories.

    Args:
        dir1:
            Directory with InsetChart.json files

        dir2:
            Directory with InsetChart.json files

        dir3:
            Directory with InsetChart.json files

        title:
            Title of Plot

        show_raw_data:
            If true, shows the raw/individual simulation data in a lighter color.

        subplot_index_min:
            The index of the first subplot to show based on the alphabetical
            order of the channels in the report.

        subplot_index_min:
            The index of the last subplot to show based on the alphabetical
            order of the channels in the report.

        output:
            If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.

    Return:
        None, if output is provided, an image will be saved to the output directory, else a window will be opened.
    """
    dir_names = []
    mean_data = []
    raw_data_lists = []

    if dir1 is not None:
        dir_names.append(dir1)
        mean_cr_1, raw_data_list_1 = calculate_mean(dir1)
        mean_data.append(mean_cr_1)
        raw_data_lists.append(raw_data_list_1)

    if dir2 is not None:
        dir_names.append(dir2)
        mean_cr_2, raw_data_list_2 = calculate_mean(dir2)
        mean_data.append(mean_cr_2)
        raw_data_lists.append(raw_data_list_2)

    if dir3 is not None:
        dir_names.append(dir3)
        mean_cr_3, raw_data_list_3 = calculate_mean(dir3)
        mean_data.append(mean_cr_3)
        raw_data_lists.append(raw_data_list_3)

    plot_name = title
    if plot_name is None:
        plot_name = "InsetChart_Compare"

    if title is None:
        title = "" + pic.create_title_string(reference=None, data_filenames=dir_names)

    if not show_raw_data:
        raw_data_lists = None

    pic.plot_data(title=title,
                  ref_data=None,
                  test_data=mean_data,
                  raw_data_list_of_lists=raw_data_lists,
                  test_filenames=dir_names,
                  subplot_index_min=subplot_index_min,
                  subplot_index_max=subplot_index_max,
                  img_dir=output,
                  plot_name=plot_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir1', default=None, nargs='?', help='Directory, or parent directory that contains subdirectories, of InsetChart.json files')
    parser.add_argument('dir2', default=None, nargs='?', help='Directory, or parent directory that contains subdirectories, of InsetChart.json files')
    parser.add_argument('dir3', default=None, nargs='?', help='Directory, or parent directory that contains subdirectories, of InsetChart.json files')
    parser.add_argument('-r', '--raw', help='If provided, shows the raw/individual simulation data in a lighter color.', action='store_true')
    parser.add_argument('-m', '--subplot_index_min', default=0, type=int, help='Index of the first subplot to show.')
    parser.add_argument('-x', '--subplot_index_max', default=100, type=int, help='Index of the last subplot to show.')
    parser.add_argument('-t', '--title', default=None, help='Title of Plot')
    parser.add_argument('-o', '--output', default=None, help='If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    if args.subplot_index_min >= args.subplot_index_max:
        print("Error: subplot_index_min must be less than subplot_index_max.")
        sys.exit()

    plot_mean(dir1=args.dir1,
              dir2=args.dir2,
              dir3=args.dir3,
              title=args.title,
              show_raw_data=args.raw,
              subplot_index_min=args.subplot_index_min,
              subplot_index_max=args.subplot_index_max,
              output=args.output)
