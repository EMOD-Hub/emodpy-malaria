#!/usr/bin/python

"""
This module contains methods for plotting channel reports (i.e. InsetChart).
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np
import json
import sys
import os
import pylab
from math import sqrt, ceil


def get_raw_color(idx: int):
    """
    When plotting the raw data as background, use a lighter color than the test data.
    Needs to be synchronized with get_color_name().

    Args:
        idx:
            index of the plot used to select color

    Returns:
        Matplotlib basic color to use for plotting.
    """
    colors = [('blue', 0.1),
              ('green', 0.1),
              ('cyan', 0.1),
              ('magenta', 0.1),
              ('yellow', 0.1),
              ('black', 0.1)]
    return colors[idx % len(colors)]


def get_color_name(idx: int):
    """
    Return name of color that should be returned by getColor() given the same input value.
    Needs to be synchronized with get_raw_color().

    Args:
        idx:
            index of the plot used to select color

    Returns:
        Name of the basic color to use for plotting in matplotlib.
    """
    color_names = ['blue', 'green', 'cyan', 'magenta', 'yellow', 'black']
    return color_names[idx % len(color_names)]


def get_list_of_channels(ref_data: dict, test_data: list[dict]):
    """
    Returns a list of the unique channel names used in both the reference data
    and the test data.  This should enable the display of all of the channels
    even when both reports do not have the same channels.

    Args:
        ref_data:
            channel report, json dictionary consider to contain the baseline data

        test_data:
            a list of channel reports (dictionaries) containing data to compare to

    Returns:
        Unique list of channels from all the channels in the input
    """

    channel_titles_list = []
    if ref_data is not None:
        channel_titles_list = list(ref_data["Channels"].keys())

    for data in test_data:
        channel_titles_list = channel_titles_list + list(data["Channels"].keys())

    channel_titles_set = set(channel_titles_list)
    channel_titles_list = sorted(list(channel_titles_set))

    return channel_titles_list


def create_title_string(reference: str, data_filenames: list[str]):
    """
    Returns a string that contains the input file names where the color used
    in plotting is included in the name.  This can be used as the title of the plot.

    Args:
        reference:
            name of the reference data file

        data_filenames:
            a list of the test data file names

    Returns:
        A string where each file name is on its own line and includes the color
        to be used in plotting in the name.
    """
    title = ""
    if reference is not None:
        title = "reference(red)=" + reference + "\n"

    for i, filename in enumerate(data_filenames):
        color_name = get_color_name(i)
        title = title + "test(" + color_name + ")=" + filename
        if i < (len(data_filenames) - 1):
            title = title + "\n"

    return title


def get_data_from_directory(directory: str):
    """
    Gets the JSON files from the input directory and return the names of the files
    and the dictionaries of data.  The idea is to allow the user to put several
    channel reports into one directory and plot them all by just giving the name
    of the directory.

    Args:
        directory:
            a path to a directory that contains only a collection of channel reports

    Returns:
        Return the list of file names in the directory AND the list of dictionaries
        containing the data of those files
    """
    dir_data = []
    dir_data_filenames = []
    for file in os.listdir(directory):
        file = os.path.join(directory, file)
        if file.endswith(".json"):
            dir_data_filenames.append(file)

    dir_data_filenames = sorted(dir_data_filenames)
    for file in dir_data_filenames:
        with open(file) as dir_sim:
            dir_data.append(json.loads(dir_sim.read()))

    return dir_data_filenames, dir_data


def plot_subplot(chan_title: str,
                 data: dict,
                 color: str,
                 linewidth: int,
                 subplot: plt.Axes):
    if chan_title in data["Channels"]:
        tstep = 1
        if "Simulation_Timestep" in data["Header"]:
            tstep = data["Header"]["Simulation_Timestep"]
        x_len = len(data["Channels"][chan_title]["Data"])
        x_data = np.arange(0, (x_len * tstep), tstep)
        y_data = data["Channels"][chan_title]["Data"]
        subplot.plot(x_data, y_data, color=color, linewidth=linewidth)
    else:
        print("Raw Data missing channel = " + chan_title)


def plot_data(title: str,
              ref_data: dict = None,
              test_data: list[dict] = None,
              raw_data_list_of_lists: list[list[dict]] = None,
              test_filenames: list[str] = None,
              subplot_index_min: int = 0,
              subplot_index_max: int = 100,
              img_dir: str = None,
              plot_name: str = None):
    """
    Plot the data such that there is a grid of subplots with each subplot representing
    a "channel" of data.  Each subplot will have time on the x-axis and the units of
    that channel on the y-axis.

    Args:
        title:
            The string to put at the top of the page

        ref_data:
            A channel report dictionary whose data will be plotted in red

        test_data:
            A list of channel report dictionaries whose data will be plotted
            in colors other than red
        test_file_names:
            The list of file names in parallel to the test_data.

        subplot_index_min:
            The index of the first subplot to show based on the alphabetical
            order of the channels in the report.

        subplot_index_min:
            The index of the last subplot to show based on the alphabetical
            order of the channels in the report.

        img_dir:
            The name of the directory to save the images to.  If not provided, it will open a window.

        plot_name:
            If provided the name of the file for the saved image.

    Returns:
        Nothing
    """
    if test_filenames is None:
        test_filenames = []

    if img_dir is not None:
        plt.figure(figsize=(24, 13))

    channel_titles_list = get_list_of_channels(ref_data, test_data)

    num_chans = len(channel_titles_list)
    if subplot_index_max >= num_chans:
        subplot_index_max = num_chans - 1
    num_chans = subplot_index_max - subplot_index_min + 1

    square_root = ceil(sqrt(num_chans))
    # Explicitly perform a float division here as integer division floors in Python 2.x
    n_figures_y = ceil(float(num_chans) / float(square_root))
    n_figures_x = square_root

    ref_color = "red"
    if len(test_data) == 0:
        ref_color = "blue"

    idx = -1
    for subplot_index, chan_title in enumerate(channel_titles_list):
        if (subplot_index < subplot_index_min) or (subplot_index > subplot_index_max):
            continue
        idx += 1
        idx_x = idx % n_figures_x
        idx_y = int(idx / n_figures_x)

        try:
            subplot = plt.subplot2grid((n_figures_y, n_figures_x), (idx_y, idx_x))

            if raw_data_list_of_lists is not None:
                for list_index, raw_data_list in enumerate(raw_data_list_of_lists):
                    raw_color = get_raw_color(list_index)
                    for raw_data in raw_data_list:
                        plot_subplot(chan_title=chan_title,
                                     data=raw_data,
                                     color=raw_color,
                                     linewidth=1,
                                     subplot=subplot)

            if ref_data is not None:
                plot_subplot(chan_title=chan_title,
                             data=ref_data,
                             color=ref_color,
                             linewidth=2,
                             subplot=subplot)

            for test_idx, data in enumerate(test_data):
                tst_color = get_color_name(test_idx)
                plot_subplot(chan_title=chan_title,
                             data=data,
                             color=tst_color,
                             linewidth=1,
                             subplot=subplot)

            plt.setp(subplot.get_xticklabels(), fontsize='7')
            plt.title(chan_title, fontsize='9')
        except Exception as ex:
            print("Exception: " + str(ex))

    plt.suptitle(title)

    plt.subplots_adjust(left=0.04, right=0.99, bottom=0.04, top=0.9, wspace=0.3, hspace=0.3)

    if img_dir:
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        plot_name = plot_name.replace(" ", "_")
        plot_name = plot_name.replace("\n", "_")
        fn = os.path.join(img_dir, plot_name + ".png")
        print(fn)
        pylab.savefig(fn, dpi=300, orientation='landscape')
    else:
        plt.show()
    plt.close()

    return


def plot_inset_chart(dir_name: str = None,
                     reference: str = None,
                     comparison1: str = None,
                     comparison2: str = None,
                     comparison3: str = None,
                     title: str = None,
                     include_filenames_in_title=True,
                     output: str = None):
    """
    Plot the inset chart using the provided parameters.

    Args:
        dir_name:
            Directory containing channel reports with .json extension

        reference:
            Reference channel report filename

        comparison1:
            Comparison1 channel report filename

        comparison2:
            Comparison2 channel report filename

        comparison3:
            Comparison3 channel report filename

        title:
            Title of Plot

        include_filenames_in_title:
            If true, includes the filenames in the title (needed for testing)

        output:
            If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.

    Returns:
        Nothing
    """
    test_filenames = []
    test_data = []
    if dir_name is not None:
        test_filenames, test_data = get_data_from_directory(dir_name)

    if comparison1 is not None:
        test_filenames.append(comparison1)
        with open(comparison1) as test_sim:
            test_data.append(json.loads(test_sim.read()))

    if comparison2 is not None:
        test_filenames.append(comparison2)
        with open(comparison2) as test_sim:
            test_data.append(json.loads(test_sim.read()))

    if comparison3 is not None:
        test_filenames.append(comparison3)
        with open(comparison3) as test_sim:
            test_data.append(json.loads(test_sim.read()))

    ref_data = None
    if reference is not None:
        with open(reference) as ref_file:
            ref_data = json.loads(ref_file.read())

    plot_name = title
    if plot_name is None:
        plot_name = "InsetChart"

    if title is None:
        title = ""
    if include_filenames_in_title:
        num_files = 0
        if reference is not None:
            num_files = 1
        num_files = num_files + len(test_filenames)
        if (num_files > 4) and (dir_name is not None):
            title = title + "\n" + dir_name
        else:
            title = title + "\n" + create_title_string(reference, test_filenames)

    plot_data(title=title,
              ref_data=ref_data,
              test_data=test_data,
              img_dir=output,
              plot_name=plot_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('reference', default=None, nargs='?', help='Reference InsetChart filename')
    parser.add_argument('comparison1', default=None, nargs='?', help='Comparison1 InsetChart filename')
    parser.add_argument('comparison2', default=None, nargs='?', help='Comparison2 InsetChart filename')
    parser.add_argument('comparison3', default=None, nargs='?', help='Comparison3 InsetChart filename')
    parser.add_argument('-d', '--dir', default=None, nargs='?', help='Directory of InsetChart.json files')
    parser.add_argument('-t', '--title', default=None, nargs='?', help='Title of Plot')
    parser.add_argument('-o', '--output', default=None, help='If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    plot_inset_chart(dir_name=args.dir,
                     reference=args.reference,
                     comparison1=args.comparison1,
                     comparison2=args.comparison2,
                     comparison3=args.comparison3,
                     title=args.title,
                     output=args.output)
