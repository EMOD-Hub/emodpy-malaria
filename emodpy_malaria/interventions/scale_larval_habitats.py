from emod_api import schema_to_class as s2c
import pandas as pd
from emodpy_malaria.interventions.outbreak import add_campaign_event


def add_scale_larval_habitats(campaign, df=None,
                              start_day: int = 0, repetitions: int = 1,
                              timesteps_between_repetitions: int = 365):
    """
    Reduce available larval habitat in a node-specific way.

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        df: The dataframe containing habitat scale factors. **Examples**::

            Scale TEMPORARY_RAINFALL by 3-fold for all nodes, all species:
            df = pd.DataFrame({ 'TEMPORARY_RAINFALL': [3]})

            Scale TEMPORARY_RAINFALL by 3-fold for all nodes, arabiensis only:
            df = pd.DataFrame({ 'TEMPORARY_RAINFALL.arabiensis': [3]})

            Scale differently by node ID:
            df = pd.DataFrame({ 'NodeID' : [0, 1, 2, 3, 4],
                                'CONSTANT': [1, 0, 1, 1, 1],
                                'TEMPORARY_RAINFALL': [1, 1, 0, 1, 0]})

            Scale differently by both node ID and species:
            df = pd.DataFrame({ 'NodeID' : [0, 1, 2, 3, 4],
                                'CONSTANT.arabiensis': [1, 0, 1, 1, 1],
                                'TEMPORARY_RAINFALL.arabiensis': [1, 1, 0, 1, 0],
                                'CONSTANT.funestus': [1, 0, 1, 1, 1]})

            Scale some habitats by species and others same for all species:
            df = pd.DataFrame({ 'NodeID' : [0, 1, 2, 3, 4],
                                'CONSTANT.arabiensis': [1, 0, 1, 1, 1],
                                'TEMPORARY_RAINFALL.arabiensis': [1, 1, 0, 1, 0],
                                'CONSTANT.funestus': [1, 0, 1, 1, 1],
                                'LINEAR_SPLINE': [1, 1, 0, 1, 0]})

            Scale nodes at different dates:
            df = pd.DataFrame({  'NodeID' : [0, 1, 2, 3, 4],
                                 'CONSTANT': [1, 0, 1, 1, 1],
                                 'TEMPORARY_RAINFALL': [1, 1, 0, 1, 0],
                                 'Start_Day': [0, 30, 60, 65, 65]
                                 })

        start_day: The date that habitats are scaled for all scaling
            actions specified in **df**. Used only if there is no
            Start_Day column in **df**.
        repetitions: The number of times to repeat the intervention.
        timesteps_between_repetitions: The number of time steps between
            repetitions.

    Returns:
        None
    """

    if 'Start_Day' not in df.columns.values:
        df['Start_Day'] = start_day

    standard_columns = ['NodeID', 'Start_Day']
    habitat_columns = [x for x in df.columns.values if x not in standard_columns]
    habitat_names = list(set([x.split('.')[0] for x in habitat_columns]))
    by_species = any(['.' in x for x in df.columns.values if x not in standard_columns])
    by_node = 'NodeID' in df.columns.values

    for start_day, df_by_date in df.groupby('Start_Day'):
        for gn, gdf in df_by_date.groupby(habitat_columns):
            habitat_scales = []
            if not by_species:
                if len(habitat_names) == 1:
                    habitat_scales.append({"Habitat": habitat_columns[0],
                                           "Species": "ALL_SPECIES",
                                           "Factor": float(gn[0])})
                else:
                    for x, y in zip(habitat_columns, gn):
                        habitat_scales.append({"Habitat": x,
                                               "Species": "ALL_SPECIES",
                                               "Factor": float(y)})

            else:
                if len(habitat_names) == 1:
                    if len(habitat_columns) == 1:
                        habitat, sp = habitat_columns[0].split('.')
                        habitat_scales.append({"Habitat": habitat,
                                               "Species": sp,
                                               "Factor": float(gn[0])})
                    else:
                        habitat = habitat_columns[0].split('.')[0]
                        species = [x.split('.')[1] for x in habitat_columns]
                        for sp, x in zip(species, gn):
                            habitat_scales.append({"Habitat": habitat,
                                                   "Species": sp,
                                                   "Factor": float(x)})
                else:
                    for ih, habitat in enumerate(habitat_names):
                        if habitat in habitat_columns:
                            habitat_scales.append({"Habitat": habitat,
                                                   "Species": "ALL_SPECIES",
                                                   "Factor": float(gdf.iloc[0][habitat])})
                        else:
                            h = [x for x in habitat_columns if habitat in x]
                            vals = [gn[x] for x in range(len(habitat_columns)) if habitat in habitat_columns[x]]
                            for x, y in zip(h, vals):
                                habitat_scales.append({"Habitat": habitat,
                                                       "Species": x.split('.')[1],
                                                       "Factor": float(y)})

            if by_node:
                node_ids = [int(x) for x in gdf['NodeID']]
            else:
                node_ids = None

            add_habitat_reduction_event(campaign, start_day=start_day, node_ids=node_ids, habitat_scales=habitat_scales,
                                        repetitions=repetitions,
                                        timesteps_between_repetitions=timesteps_between_repetitions)


def add_habitat_reduction_event(campaign, start_day: int, node_ids: list, habitat_scales: list, repetitions: int,
                                timesteps_between_repetitions: int):
    """
        Add a campaign event to reduce vector's larval habitat(s).

    Args:
        campaign: campaign object to which the intervention will be added, and schema_path container
        start_day: The day the intervention is given out.
        node_ids: List of nodes to which to distribute the intervention. [] or None, indicates all nodes
            will get the intervention
        habitat_scales: List of dictionaries for scaling larval habitats.
            Examples::

                [{"Habitat": "ALL_HABITATS", "Species": "ALL_SPECIES", "Factor": 0.5},
                {"Habitat": "CONSTANT", "Species": "arabiensis", "Factor": 2}]

        repetitions: The number of times an intervention is given, used with timesteps_between_repetitions. -1 means
            the intervention repeats forever. Sets **Number_Repetitions**
        timesteps_between_repetitions: The interval, in timesteps, between repetitions. Ignored if repetitions = 1.
            Sets **Timesteps_Between_Repetitions**

    Returns:
        Nothing
    """

    # configuring the intervention itself
    scale_larval_habitat_intervention = s2c.get_class_with_defaults("ScaleLarvalHabitat", campaign.schema_path)
    # scale_larval_habitat_intervention.Larval_Habitat_Multiplier = larval_habitat_multiplier_list
    scale_larval_habitat_intervention.Larval_Habitat_Multiplier = habitat_scales

    add_campaign_event(campaign=campaign, start_day=start_day, node_ids=node_ids, repetitions=repetitions,
                       timesteps_between_repetitions=timesteps_between_repetitions,
                       intervention=scale_larval_habitat_intervention)
