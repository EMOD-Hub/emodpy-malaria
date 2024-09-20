"""
This module contains the classes and functions for creating demographics files
for malaria simulations. For more information on |EMOD_s| demographics files,
see :doc:`emod-malaria:software-demographics`. 
"""
import os
import emod_api.demographics.Demographics as Demog
from emod_api.demographics import DemographicsTemplates as DT
import emod_api.config.default_from_schema_no_validation as dfs

class MalariaDemographics(Demog.Demographics):
    """
    This class is derived from :py:class:`emod_api:emod_api.demographics.Demographics.Demographics` 
    and sets certain defaults for malaria in construction.

    Args:
        nodes: The number of nodes to create.
        idref: Method describing how the latitude and longitude values are created
            for each of the nodes in a simulation. "Gridded world" values use a grid 
            overlaid across the globe at some arcsec resolution. You may also generate 
            the grid using another tool or coordinate system. For more information,
            see :ref:`emod-malaria:demo-metadata`.
        base_file: A basic demographics file used as a starting point for
            creating more complicated demographics files. For example,
            using a single node file to create a multi-node file for spatial
            simulations. 
        init_prev: The initial malaria prevalence of the population. Defaults to 0%.
        include_biting_heterogeneity: variable biting rates. Defaults to on.

    Returns: 
        None 
     """
    def __init__(self, nodes, idref="Gridded world grump2.5arcmin", base_file=None, init_prev=0.0, include_biting_heterogeneity=True):
        super().__init__( nodes, idref, base_file )
        super().SetDefaultNodeAttributes(birth=True)
        if init_prev > 0:
            # Do constant intial prevalence as uniform with same min and max.
            super().SetInitPrevFromUniformDraw( init_prev, init_prev, f"Constant Initial Prevalence ({init_prev})"  )
        if include_biting_heterogeneity:
            self.set_risk_lowmedium() # lognormal, default=1.6

    def set_risk_lowmedium( self ):
        """
            Set initial risk for low-medium transmission settings per: 
            https://wiki.idmod.org/display/MAL/Heterogeneous+biting+risk+in+simulations+vs+data.
        """
        super().SetHeteroRiskLognormalDist( mean=0.0, sigma=1.6 )

    def set_risk_high( self ):
        """
            Set initial risk for high transmission settings per: 
            https://wiki.idmod.org/display/MAL/Heterogeneous+biting+risk+in+simulations+vs+data.
        """
        super().SetHeteroRiskExponDist( mean=1.0 ) # 1.0 is placeholder

    def add_larval_habitat_multiplier( self, schema, hab_type, multiplier, species="ALL_SPECIES", node_id=0 ):
        """
            Add LarvalHabitatMultiplier to node(s).

            Args:
                schema: Path to schema.json.
                hab_type: Habitat type.
                multiplier: Multiplier or Factor.
                specices: Specific species (defaults to ALL).
                node_id: Nodes for this LHM. Defaults to all.

            Returns:
                Nothing.

        """

        lhm = dfs.schema_to_config_subnode( schema, [ "idmTypes", "idmType:LarvalHabitatMultiplierSpec" ] )
        lhm.parameters.Factor = multiplier
        lhm.parameters.Habitat = hab_type
        lhm.parameters.Species = species
        lhm.parameters.finalize()

        # set params
        if node_id == 0:
            if "LarvalHabitatMultiplier" in self.raw['Defaults']['NodeAttributes']:
                lhm_dict = self.raw['Defaults']['NodeAttributes']["LarvalHabitatMultiplier"]
            else:
                lhm_dict = []
            lhm_dict.append( lhm.parameters )
            self.SetNodeDefaultFromTemplate( { "LarvalHabitatMultiplier": lhm_dict }, setter_fn = None )
        else:
            if self.get_node(node_id).node_attributes.larval_habitat_multiplier:
                lhm_dict = self.get_node(node_id).node_attributes.larval_habitat_multiplier
            else:
                lhm_dict = []
            lhm_dict.append( lhm.parameters )
            self.get_node(node_id).node_attributes.larval_habitat_multiplier = lhm_dict

def from_template_node(lat=0, lon=0, pop=1e6, name=1, forced_id=1, init_prev=0.2, include_biting_heterogeneity=True):
    """
    Create a single-node :py:class:`~emodpy_malaria.demographics.MalariaDemographics`
    instance from the parameters you supply.

    Args:
        lat: Latitude of the centroid of the node to create.
        lon: Longitude of the centroid of the node to create.
        pop: Human population of the node. 
        name: The name of the node. This may be a characteristic of the 
            node, such as "rural" or "urban", or an identifying integer.
        forced_id: The node ID for the single node.
        init_prev: The initial malaria prevalence of the node.

    Returns:
        A :py:class:`~emodpy_malaria.demographics.MalariaDemographics` instance.
    """
    new_nodes = [Demog.Node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id) ]
    return MalariaDemographics(nodes=new_nodes, init_prev=init_prev, include_biting_heterogeneity=include_biting_heterogeneity)

def from_pop_csv( pop_filename_in, pop_filename_out="spatial_gridded_pop_dir", site="No_Site" ):
    """
    Create a multi-node :py:class:`~emodpy_malaria.demographics.MalariaDemographics`
    instance from a CSV file describing a population.

    Args:
        pop_filename_in: The path to the demographics file to ingest.
        pop_filename_out: The path to the file to output.
        site: A string to identify the country, village, or trial site.

    Returns:
        A :py:class:`~emodpy_malaria.demographics.MalariaDemographics` instance
    """
    if os.path.exists( pop_filename_in ) == False:
        raise ValueError( f"Can't find input data file {pop_filename_in}" )

    generic_demog = Demog.from_pop_csv( pop_filename_in, pop_filename_out, site )
    nodes = generic_demog._nodes
    return MalariaDemographics(nodes=nodes, idref=site)

def from_csv(input_file, res=30/3600, id_ref="from_csv", init_prev=0.0, include_biting_heterogeneity=True):
    """
    Create a multi-node :py:class:`~emodpy_malaria.demographics.MalariaDemographics`
    instance from a CSV file describing a population.

    Args:
        input_file: The path to the csv file to ingest.
        res: Resolution.
        id_ref: A string to identify the file, needs to match other input files.
        init_prev: The initial malaria prevalence of the population. Defaults to 0%.
        include_biting_heterogeneity: variable biting rates. Defaults to on.

    Returns:
        A :py:class:`~emodpy_malaria.demographics.MalariaDemographics` instance
    """
    if os.path.exists( input_file ) == False:
        raise ValueError( f"Can't find input data file {input_file}" )

    generic_demog = Demog.from_csv( input_file, res, id_ref )
    nodes = generic_demog._nodes
    return MalariaDemographics(nodes=nodes, idref=id_ref, init_prev=init_prev, include_biting_heterogeneity=include_biting_heterogeneity)

def from_params(tot_pop=1e6, num_nodes=100, frac_rural=0.3, id_ref="from_params" ):
    """
    Create a multi-node :py:class:`~emodpy_malaria.demographics.MalariaDemographics`
    instance as a synthetic population based on a few parameters.

    Args:
        tot_pop: The total human population in the node.
        num_nodes: The number of nodes to create.
        frac_rural: The fraction of the population that is rural.
        id_ref: Method describing how the latitude and longitude values are created
            for each of the nodes in a simulation. "Gridded world" values use a grid 
            overlaid across the globe at some arcsec resolution. You may also generate 
            the grid using another tool or coordinate system. For more information,
            see :ref:`emod-malaria:demo-metadata`.

    Returns:
        A :py:class:`~emodpy_malaria.demographics.MalariaDemographics` instance.
    """
    generic_demog = Demog.from_params(tot_pop, num_nodes, frac_rural, id_ref )
    nodes = generic_demog.nodes
    return MalariaDemographics(nodes=nodes, idref=id_ref )

