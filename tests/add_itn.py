#!/usr/bin/env python

import emodpy_malaria.interventions.bednet as itn
import emodpy_malaria.interventions as comm
import emod_api.campaign as camp

for cvg, min_age, max_age in coverage_by_age_tuple:
    camp.add(comm.triggered_campaign_delay_event(camp, 1, "NewInfection", { "Delay_Period_Constant": 25 }, itn.BednetIntervention(), cvg, min_age, max_age))
