#!/usr/bin/python

from scipy import stats
import math

from idm_test.dtk_test.sft_class import SFT, arg_parser
from idm_test.dtk_test.general_support import parse_inset_chart, ConfigKeys
import idm_test.plot as idm_plot
from idm_test.dtk_test.std_out import SearchType

"""
spec: TBD

This is a test for Microsporidia_Duration_To_Disease_Simple 

output:
Infectiousness.png 

"""


class MicrosporidiaDurationToDisease(SFT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_report_name = "InsetChart.json"
        self.params_keys = [ConfigKeys.Simulation_Duration]

    def load_config(self):
        super(MicrosporidiaDurationToDisease, self).load_config(params_keys=self.params_keys)

    # overwrite the test method
    def test(self):
        self.msg.append('Start testing: \n')

        inf_vectors = "Infectious Vectors"
        adult_vectors = "Adult Vectors"
        hum_inf_reserv = "Human Infectious Reservoir"
        relevant_data = parse_inset_chart(insetkey_list=[inf_vectors, hum_inf_reserv, adult_vectors])

        # checking that at the beginning we have non-zero vectors, infectious vectors, and human infectious reservoir
        adult_vectors_at_check_step = 3000
        close_enough = 0.05
        check_step = 100
        if abs(relevant_data[adult_vectors][
                   check_step] - adult_vectors_at_check_step) / adult_vectors_at_check_step > close_enough:
            self.success = False
            self.msg.append(
                f"Bad: Based on previous runs we expect about {adult_vectors_at_check_step} {adult_vectors} at "
                f"timestep {check_step}, but {relevant_data[adult_vectors][check_step]} is a bit far from that.\n")
        elif relevant_data[inf_vectors][check_step] == 0:
            self.success = False
            self.msg.append(f"Bad: Based on previous runs we expect about there to be some {inf_vectors} at "
                            f"timestep {check_step}, but we have 0.\n")
        elif relevant_data[hum_inf_reserv][check_step] == 0:
            self.success = False
            self.msg.append(f"Bad: Based on previous runs we expect about there to be a positive presence in "
                            f"{hum_inf_reserv} at timestep {check_step}, but we have 0.\n")

        # checking that at the end we still have vectors, but no infectious vectors and no human infectious reservoir
        check_step = 699
        adult_vectors_at_check_step = 4600
        if abs(relevant_data[adult_vectors][
                   check_step] - adult_vectors_at_check_step) / adult_vectors_at_check_step > close_enough:
            self.success = False
            self.msg.append(
                f"Bad: Based on previous runs we expect about {adult_vectors_at_check_step} {adult_vectors} "
                f"at timestep {check_step}, but {relevant_data[adult_vectors][check_step]} is a bit far from "
                f"that.\n")
        elif relevant_data[inf_vectors][check_step] != 0:
            self.success = False
            self.msg.append(f"Bad: Based on previous runs we expect about there to be no {inf_vectors} at "
                            f"timestep {check_step}, but we have {relevant_data[inf_vectors][check_step]}.\n")
        elif relevant_data[hum_inf_reserv][check_step] != 0:
            self.success = False
            self.msg.append(f"Bad: Based on previous runs we expect about there to be a nothing in "
                            f"{hum_inf_reserv} at timestep {check_step}, but we have "
                            f"{relevant_data[hum_inf_reserv][check_step]}.\n")

        pass


def application(output_folder="output", my_arg=None):
    if not my_arg:
        my_sft = MicrosporidiaDurationToDisease(stdout='stdout.txt')
    else:
        my_sft = MicrosporidiaDurationToDisease(
            output=my_arg.output, stdout='stdout.txt', json_report=my_arg.json_report, event_csv=my_arg.event_csv,
            config=my_arg.config, campaign=my_arg.campaign, report_name=my_arg.report_name, debug=my_arg.debug)
    my_sft.run()


if __name__ == "__main__":
    # execute only if run as a script
    my_arg = arg_parser()
    application(my_arg=my_arg)
