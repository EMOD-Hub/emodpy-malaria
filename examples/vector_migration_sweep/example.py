"""
Sweep x_vector_migration across [0.5, 1.0, 1.5].

x_vector_migration scales how frequently vectors move between nodes.
Lower values confine vectors to their home node; higher values increase
dispersal and can spread infection across a wider area.

This example runs a 3-node spatial simulation and produces one set of
simulations per x_vector_migration value (plus stochastic replicates via
Run_Number). Results include InsetChart and ReportVectorMigrationTracking
so you can compare total migration events across the sweep.
"""
import os
import pathlib

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from emodpy.emod_task import EMODTask

import manifest

sim_years = 1


def sweep_x_vector_migration(simulation, x_vector_migration):
    """Sets x_Vector_Migration on the gambiae species config."""
    from emodpy_malaria.vector_config import get_species_params
    sp = get_species_params(simulation.task.config, "gambiae")
    sp.x_Vector_Migration = x_vector_migration
    return {"x_vector_migration": x_vector_migration}


def build_config(config):
    import emodpy_malaria.malaria_config as malaria_config

    config = malaria_config.set_team_defaults(config, manifest)
    malaria_config.add_species(config, manifest, ["gambiae"])

    config.parameters.Run_Number = 0
    config.parameters.Simulation_Duration = sim_years * 365

    return config


def build_demographics():
    from emod_api.demographics.node import Node
    from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
    from emodpy_malaria.utils.distributions import UniformDistribution
    from emodpy_malaria.utils.emod_enum import BirthRateDependence
    from emodpy_malaria.migration import VectorMigrationData

    nodes = [
        Node(lat=-2.0, lon=32.0, pop=5000, forced_id=1, name="Village_A"),
        Node(lat=-2.1, lon=32.2, pop=2000, forced_id=2, name="Village_B"),
        Node(lat=-2.3, lon=32.5, pop=500,  forced_id=3, name="Village_C"),
    ]
    demog = MalariaDemographics(nodes=nodes, idref="vector_migration_sweep")
    demog.set_birth_rate(40, birth_rate_dependence=BirthRateDependence.POPULATION_DEP_RATE)
    demog.set_age_distribution(UniformDistribution(0, 60))

    vector_rates = {
        (1, 2): 0.01, (2, 1): 0.01,
        (1, 3): 0.005, (3, 1): 0.005,
        (2, 3): 0.008, (3, 2): 0.008,
    }
    vector_mig = VectorMigrationData.from_rates(rates=vector_rates,
                                                idref="vector_migration_sweep")

    # x_vector_migration is swept per-simulation via sweep_x_vector_migration;
    # the migration file content is the same for all sweep values
    demog.add_vector_migration(
        data=vector_mig,
        species="gambiae",
    )

    return demog


def build_campaign(campaign):
    from emodpy_malaria.campaign.individual_intervention import AntimalarialDrug
    from emodpy_malaria.campaign.distributor import add_intervention_triggered
    from emodpy.campaign.common import TargetDemographicsConfig

    campaign.set_schema(manifest.schema_file)

    drug = AntimalarialDrug(campaign, drug_type="Artemether")
    add_intervention_triggered(
        campaign,
        intervention_list=[drug],
        triggers_list=["NewClinicalCase"],
        start_day=1,
        target_demographics_config=TargetDemographicsConfig(demographic_coverage=0.5)
    )

    return campaign


def build_reports(reporters):
    from emodpy_malaria.reporters.reporters import InsetChart, ReportVectorMigration
    from emodpy.reporters.base import ReportFilter

    reporters.add(InsetChart(reporters))
    reporters.add(ReportVectorMigration(reporters,
                                        report_filter=ReportFilter(start_day=1,
                                                                   end_day=sim_years * 365)))

    return reporters


def run_sim():
    # sym_link=False: idmtools defaults to symlinks, but Windows requires Developer Mode
    # to create them. Using file copies instead works on all Windows configurations.
    platform = Platform(manifest.plat_name, job_directory=manifest.job_dir,
                        docker_image=manifest.plat_image, sym_link=manifest.sym_link)

    task = EMODTask.from_defaults(
        eradication_path=manifest.eradication_path,
        schema_path=manifest.schema_file,
        config_builder=build_config,
        campaign_builder=build_campaign,
        demographics_builder=build_demographics,
        report_builder=build_reports,
    )

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_x_vector_migration, [0.5, 1.0, 1.5])

    experiment = Experiment.from_builder(builder, task,
                                         name="vector_migration_sweep")
    experiment.run(wait_until_done=True, platform=platform)

    if experiment.succeeded:
        print(f"Experiment {experiment.id} succeeded.")
        with open("experiment_id", "w") as f:
            f.write(experiment.id)
    else:
        print(f"Experiment {experiment.id} failed.")


if __name__ == "__main__":
    import emod_malaria.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    run_sim()
