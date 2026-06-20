import pandas as pd
import numpy as np
import json
from datetime import datetime


class ChannelReport:
    """
    A class that can be used to convert an EMOD channel report/dictionary
    (i.e. InsetChart, DemographicsSummary, PropertyReport, etc) into a
    dataframe.  A static method is provided to go the other way.
    """
    def __init__(self, df: pd.DataFrame = None):
        self.json_data = self.convert_df_to_channel_report(df)

    def create_empty_channel_report(self):
        """
        Create the dictionary that has the right format for a channel report.
        It would be really nice if we could include Start_Time & Simulation_Timestep
        from the input files, but these are hardcoded for now.

        Args:

        Returns:
            (dict): A dictionary that has the header and an emtpy 'Channels' entry
        """
        report = {}
        report["Header"] = {}
        report["Header"]["DateTime"           ] = datetime.today().strftime('%Y-%m-%d') # noqa: E202
        report["Header"]["DTK_Version"        ] = "unknown"                             # noqa: E202
        report["Header"]["Report_Type"        ] = "InsetChart"                          # noqa: E202
        report["Header"]["Report_Version"     ] = "3.2"                                 # noqa: E202
        report["Header"]["Start_Time"         ] = 0                                     # noqa: E202
        report["Header"]["Simulation_Timestep"] = 365 / 12
        report["Header"]["Timesteps"          ] = 0                                     # noqa: E202
        report["Header"]["Channels"           ] = 0                                     # noqa: E202

        report["Channels"] = {}

        return report

    def add_channel(self, report, channel_name, values):
        """
        Add the values of the channel to the report

        Args:
            report (dict): a channel report formatted JSON dictionary
            channel_name (str): the name of the channel to Add
            values (list): a list of integers or floats for that channel

        Returns:
        """
        report["Channels"][channel_name] = {}
        report["Channels"][channel_name]["Units"] = ""
        report["Channels"][channel_name]["Data"] = values

        report["Header"]["Channels"] += 1

        return

    def convert_df_to_channel_report(self, df):
        """
        Convert the dataframe to a dictionary of the channel report format.

        Args:
            df (pd.DataFrame): a dataframe where the columns are the channels and there
                is a row for each time step

        Returns:
            (dict): A dictionary that contains the data from the dataframe and can be
                converted to a JSON channel report
        """
        report = self.create_empty_channel_report()

        for name, values in df.items():
            if name != "Time":
                self.add_channel(report, name, values.tolist())

        return report

    def save(self, filename):
        """
        Save this report data to a file.
        Args:
            filename: The name of the file (including path) to contain the data/JSON.

        Returns:
        """
        with open(filename, 'w') as file:
            json.dump(self.json_data, file, indent=4)
        return

    @staticmethod
    def convert_to_df(channel_report_dict, channels_to_extract=None):
        """
        Convert the input dictionary into a dataframe

        Args:
            channel_report_dict (dict):
                The name of the file (including path) to contain the data/JSON.

            channels_to_extract (list):
                A list of strings that are the channel names to extract from the
                JSON and put into the dataframe

        Returns:
            (pd.DataFrame): A dataframe where the columns are the channels of the report.
                An extra 'Time' column is added to the dataframe
        """
        dt             = channel_report_dict["Header"]["Simulation_Timestep"]  # noqa: E221
        start_time     = channel_report_dict["Header"]["Start_Time"]           # noqa: E221
        num_time_steps = channel_report_dict["Header"]["Timesteps"]

        result_dict = {"Time": start_time + (np.arange(num_time_steps) * dt)}

        if channels_to_extract is None:
            channels_to_extract = channel_report_dict["Channels"].keys()

        for channel_name in channels_to_extract:
            result_dict[channel_name] = channel_report_dict["Channels"][channel_name]["Data"]

        df = pd.DataFrame(result_dict)

        return df
