from collections import defaultdict
from datetime import datetime
from functools import partial
import json
from numbers import Integral
from os import environ, SEEK_SET
from pathlib import Path
from platform import system
from warnings import warn

import numpy as np
import csv

# for from_params()
import scipy.spatial.distance as spspd
from emod_api.demographics import Demographics as Demog

# for from_demog_and_param_gravity()
from geographiclib.geodesic import Geodesic

from emodpy_malaria.vector_config import add_vector_migration

class Layer(dict):
    """
    The Layer object represents a mapping from source node (IDs) to destination node (IDs) for a particular
    age, gender, age+gender combination, or all users if no age or gender dependence. Users will not generally
    interact directly with Layer objects.
    """

    def __init__(self):

        super().__init__()

        return

    @property
    def DatavalueCount(self) -> int:
        """Get (maximum) number of data values for any node in this layer

        Returns:
            Maximum number of data values for any node in this layer

        """
        count = max([len(entry) for entry in self.values()]) if len(self) else 0
        return count

    @property
    def NodeCount(self) -> int:
        """Get the number of (source) nodes with rates in this layer

        Returns:
            Number of (source) nodes with rates in this layer

        """
        return len(self)

    def __getitem__(self, key):
        """Allows indexing directly into this object with source node id

        Args:
            key (int): source node id

        Returns:
            Dictionary of outbound rates for the given node id
        """
        if key not in self:
            if isinstance(key, Integral):
                super().__setitem__(key, defaultdict(float))
            else:
                raise RuntimeError(f"Migration node IDs must be integer values (key = {key}).")
        return super().__getitem__(key)


_METADATA = "Metadata"
_AUTHOR = "Author"
_DATECREATED = "DateCreated"
_TOOLNAME = "Tool"
_IDREFERENCE = "IdReference"
_MIGRATIONTYPE = "MigrationType"
_NODECOUNT = "NodeCount"
_DATAVALUECOUNT = "DatavalueCount"
_GENDERDATATYPE = "GenderDataType"
_AGESYEARS = "AgesYears"
_INTERPOLATIONTYPE = "InterpolationType"
_NODEOFFSETS = "NodeOffsets"
_EMODPYMALARIA = "emodpy-malaria"


class VectorMigration(object):
    """Represents vector migration data in a mapping from source node (IDs) to destination node (IDs) with rates
    for each pairing.

    A migration file (along with JSON metadata) can be loaded from the static method Migration.from_file() and
    inspected and/or modified.
    Migration objects can be started from scratch with Migration(), and populated with appropriate source-dest rate data
    and saved to a file with the to_file() method.
    Given migration = Migration(), syntax is as follows:

    age and gender agnostic:  migration[source_id][dest_id]
    age dependent:            migration[source_id:age]          # age should be >= 0, ages > last bucket value use last bucket value
    gender dependent:         migration[source_id:gender]       # gender one of Migration.MALE or Migration.FEMALE
    age and gender dependent: migration[source_id:gender:age]   # gender one of Migration.MALE or Migration.FEMALE

    EMOD/DTK format migration files (and associated metadata files) can be written with migration.to_file(<filename>).
    EMOD/DTK format migration files (with associated metadata files) can be read with migration.from_file(<filename>).
    """

    SAME_FOR_BOTH_GENDERS = 0
    ONE_FOR_EACH_GENDER = 1

    LINEAR_INTERPOLATION = 0
    PIECEWISE_CONSTANT = 1

    LOCAL_MIGRATION = 1
    REGIONAL_MIGRATION = 3

    def __init__(self):

        self._agesyears = []
        try:
            self._author = _author()
        except Exception as ex:
            self._author = ""
        self._datecreated = datetime.now()
        self._genderdatatype = self.SAME_FOR_BOTH_GENDERS
        self._idreference = ""
        self._interpolationtype = self.PIECEWISE_CONSTANT
        self._migrationtype = self.LOCAL_MIGRATION
        self._tool = _EMODPYMALARIA
        self._create_layers()
        return

    def _create_layers(self):

        self._layers = []
        for gender in range(0, self._genderdatatype + 1):
            for age in range(0, len(self.AgesYears) if self.AgesYears else 1):
                self._layers.append(Layer())

        return

    @property
    def AgesYears(self) -> list:
        """
        List of ages - ages < first value use first bucket, ages > last value use last bucket.
        """
        return self._agesyears

    @AgesYears.setter
    def AgesYears(self, ages: list) -> None:
        """
        List of ages - ages < first value use first bucket, ages > last value use last bucket.
        """
        if sorted(ages) != self.AgesYears:
            if self.NodeCount > 0:
                warn("Changing age buckets clears existing migration information.", category=UserWarning)
            self._agesyears = sorted(ages)
            self._create_layers()
        return

    @property
    def Author(self) -> str:
        """str: Author value for metadata for this migration datafile"""
        return self._author

    @Author.setter
    def Author(self, author: str) -> None:
        self._author = author
        return

    @property
    def DatavalueCount(self) -> int:
        """int: Maximum data value count for any layer in this migration datafile"""
        count = max([layer.DatavalueCount for layer in self._layers])
        return count

    @property
    def DateCreated(self) -> datetime:
        """datetime: date/time stamp of this datafile"""
        return self._datecreated

    @DateCreated.setter
    def DateCreated(self, value) -> None:
        if not isinstance(value, datetime):
            raise RuntimeError(f"DateCreated must be a datetime value (got {type(value)}).")
        self._datecreated = value
        return

    @property
    def GenderDataType(self) -> int:
        """int: gender data type for this datafile - SAME_FOR_BOTH_GENDERS or ONE_FOR_EACH_GENDER"""
        return self._genderdatatype

    @GenderDataType.setter
    def GenderDataType(self, value: int) -> None:

        # integer value
        if value in VectorMigration._GENDER_DATATYPE_ENUMS.keys():
            value = int(value)
        # string value
        elif value in VectorMigration._GENDER_DATATYPE_LOOKUP.keys():
            value = VectorMigration._GENDER_DATATYPE_LOOKUP[value]
        else:
            expected = [f"{key}/{value}" for key, value in VectorMigration._GENDER_DATATYPE_LOOKUP.items()]
            raise RuntimeError(f"Unknown gender data type, {value}, expected one of {expected}.")

        if (self.NodeCount > 0) and (value != self._genderdatatype):
            warn("Changing gender data type clears existing migration information.", category=UserWarning)

        if value != self._genderdatatype:
            self._genderdatatype = int(value)
            self._create_layers()
        return

    @property
    def IdReference(self) -> str:
        """str: ID reference metadata value"""
        return self._idreference

    @IdReference.setter
    def IdReference(self, value: str) -> None:
        self._idreference = str(value)
        return

    @property
    def InterpolationType(self) -> int:
        """int: interpolation type for this migration data file - LINEAR_INTERPOLATION or PIECEWISE_CONSTANT"""
        return self._interpolationtype

    @InterpolationType.setter
    def InterpolationType(self, value: int) -> None:

        # integer value
        if value in VectorMigration._INTERPOLATION_TYPE_ENUMS.keys():
            self._interpolationtype = int(value)
        # string value
        elif value in VectorMigration._INTERPOLATION_TYPE_LOOKUP.keys():
            self._interpolationtype = VectorMigration._INTERPOLATION_TYPE_LOOKUP[value]
        else:
            expected = [f"{key}/{value}" for key, value in VectorMigration._INTERPOLATION_TYPE_LOOKUP.items()]
            raise RuntimeError(f"Unknown interpolation type, {value}, expected one of {expected}.")
        return

    @property
    def MigrationType(self) -> int:
        """int: migration type for this migration data file - LOCAL | REGIONAL """
        return self._migrationtype

    @MigrationType.setter
    def MigrationType(self, value: int) -> None:

        # integer value
        if value in VectorMigration._MIGRATION_TYPE_ENUMS.keys():
            self._migrationtype = int(value)
        elif value in VectorMigration._MIGRATION_TYPE_LOOKUP.keys():
            self._migrationtype = VectorMigration._MIGRATION_TYPE_LOOKUP[value]
        else:
            expected = [f"{key}/{value}" for key, value in VectorMigration._MIGRATION_TYPE_LOOKUP.items()]
            raise RuntimeError(f"Unknown migration type, {value}, expected one of {expected}.")
        return

    @property
    def Nodes(self) -> list:
        node_ids = set()
        for layer in self._layers:
            node_ids |= set(layer.keys())
        node_ids = sorted(node_ids)
        return node_ids

    @property
    def NodeCount(self) -> int:
        """int: maximum number of source nodes in any layer of this migration data file"""
        count = max([layer.NodeCount for layer in self._layers])
        return count

    def get_node_offsets(self, limit: int = 100) -> dict:
        nodes = set()
        for layer in self._layers:
            nodes |= set(key for key in layer.keys())
        count = min(self.DatavalueCount, limit)
        # offsets = {}
        # for index, node in enumerate(sorted(nodes)):
        #     offsets[node] = index * 12 * count
        offsets = {node: 12 * index * count for index, node in enumerate(sorted(nodes))}
        return offsets

    @property
    def NodeOffsets(self) -> dict:
        """dict: mapping from source node id to offset to destination and rate data in binary data"""
        return self.get_node_offsets()

    @property
    def Tool(self) -> str:
        """str: tool metadata value"""
        return self._tool

    @Tool.setter
    def Tool(self, value: str) -> None:
        self._tool = str(value)
        return

    def __getitem__(self, key):
        """allows indexing on this object to read/write rate data
        Args:
            key (slice): source node id:gender:age (gender and age depend on GenderDataType and AgesYears properties)
        Returns:
            dict for specified node/gender/age
        """
        if self.GenderDataType == VectorMigration.SAME_FOR_BOTH_GENDERS:
            if not self.AgesYears:
                # Case 1 - no gender or age differentiation - key (integer) == node id
                return self._layers[0][key]
            else:
                # Case 3 - age buckets, no gender differentiation - key (tuple or slice) == node id:age
                if isinstance(key, tuple):
                    node_id, age = key
                elif isinstance(key, slice):
                    node_id, age = key.start, key.stop
                else:
                    raise RuntimeError(f"Invalid indexing for migration - {key}")
                layer_index = self._index_for_gender_and_age(None, age)
                return self._layers[layer_index][node_id]
        else:
            if not self.AgesYears:
                # Case 2 - by gender, no age differentiation - key (tuple or slice) == node id:gender
                if isinstance(key, tuple):
                    node_id, gender = key
                elif isinstance(key, slice):
                    node_id, gender = key.start, key.stop
                else:
                    raise RuntimeError(f"Invalid indexing for migration - {key}")
                if gender not in [VectorMigration.SAME_FOR_BOTH_GENDERS, VectorMigration.ONE_FOR_EACH_GENDER]:
                    raise RuntimeError(f"Invalid gender ({gender}) for migration.")
                layer_index = self._index_for_gender_and_age(gender, None)
                return self._layers[layer_index][node_id]
            else:
                # Case 4 - by gender and age - key (slice) == node id:gender:age
                if isinstance(key, tuple):
                    node_id, gender, age = key
                elif isinstance(key, slice):
                    node_id, gender, age = key.start, key.stop, key.step
                else:
                    raise RuntimeError(f"Invalid indexing for migration - {key}")
                if gender not in [VectorMigration.SAME_FOR_BOTH_GENDERS, VectorMigration.ONE_FOR_EACH_GENDER]:
                    raise RuntimeError(f"Invalid gender ({gender}) for migration.")
                layer_index = self._index_for_gender_and_age(gender, age)
                return self._layers[layer_index][node_id]

    def _index_for_gender_and_age(self, gender: int, age: float) -> int:
        """
        Use age to determine age bucket, 0 if no age differentiation.
        Use gender data type to offset by # age buckets if gender data type is one for each gender and gender is female
        Ages < first value use first bucket, ages > last value use last bucket.
        """
        age_offset = 0
        for age_offset, edge in enumerate(self.AgesYears):
            if edge >= age:
                break
        gender_span = len(self.AgesYears) if self.AgesYears else 1
        gender_offset = gender * gender_span if self.GenderDataType == VectorMigration.ONE_FOR_EACH_GENDER else 0
        index = gender_offset + age_offset
        return index

    def __iter__(self):
        return iter(self._layers)

    _MIGRATION_TYPE_ENUMS = {
        LOCAL_MIGRATION: "LOCAL_MIGRATION",
        REGIONAL_MIGRATION: "REGIONAL_MIGRATION"
    }
    _GENDER_DATATYPE_ENUMS = {
        SAME_FOR_BOTH_GENDERS: "SAME_FOR_BOTH_GENDERS",
        ONE_FOR_EACH_GENDER: "ONE_FOR_EACH_GENDER"
    }

    _INTERPOLATION_TYPE_ENUMS = {
        LINEAR_INTERPOLATION: "LINEAR_INTERPOLATION",
        PIECEWISE_CONSTANT: "PIECEWISE_CONSTANT"
    }

    def to_file(self, binaryfile: Path, metafile: Path = None, value_limit: int = 100):
        """Write current data to given file (and .json metadata file)

        Args:
            binaryfile (Path): path to output file (metadata will be written to same path with ".json" appended)
            metafile (Path): override standard metadata file naming
            value_limit (int): limit on number of destination values to write for each source node (default = 100)

        Returns:
            (Path): path to binary file
        """
        binaryfile = Path(binaryfile).absolute()
        metafile = metafile if metafile else binaryfile.parent / (binaryfile.name + ".json")

        actual_datavalue_count = min(self.DatavalueCount, value_limit)  # limited to 100 destinations

        node_ids = set()
        for layer in self._layers:
            node_ids |= set(layer.keys())
        node_ids = sorted(node_ids)

        offsets = self.get_node_offsets(actual_datavalue_count)
        node_offsets_string = ''.join([f"{node:08x}{offsets[node]:08x}" for node in sorted(offsets.keys())])

        metadata = {
            _METADATA: {
                _AUTHOR: self.Author,
                _DATECREATED: f"{self.DateCreated:%a %b %d %Y %H:%M:%S}",
                _TOOLNAME: self.Tool,
                _IDREFERENCE: self.IdReference,
                _MIGRATIONTYPE: self._MIGRATION_TYPE_ENUMS[self.MigrationType],
                _NODECOUNT: self.NodeCount,
                _DATAVALUECOUNT: actual_datavalue_count
            },
            _NODEOFFSETS: node_offsets_string
        }
        if self.AgesYears:
            # older versions of Eradication do not handle empty AgesYears lists robustly
            metadata[_METADATA][_AGESYEARS] = self.AgesYears

        # "Writing metadata to '{metafile}'
        with metafile.open("w") as handle:
            json.dump(metadata, handle, indent=4, separators=(",", ": "))

        def key_func(k, d=None):
            return d[k]

        # layers are in age bucket order by gender, e.g. male 0-5, 5-10, 10+, female 0-5, 5-10, 10+
        # see _index_for_gender_and_age()
        # "Writing binary data to '{binaryfile}'
        with binaryfile.open("wb") as file:
            for layer in self:
                for node in node_ids:
                    destinations = np.zeros(actual_datavalue_count, dtype=np.uint32)
                    rates = np.zeros(actual_datavalue_count, dtype=np.float64)
                    if node in layer:

                        # Sort keys descending on rate and ascending on node ID.
                        # That way if we are truncating the list, we include the "most important" nodes.
                        keys = sorted(layer[node].keys())  # sorted ascending on node ID
                        keys = sorted(keys, key=partial(key_func, d=layer[node]), reverse=True)  # descending on rate

                        if len(keys) > actual_datavalue_count:
                            keys = keys[0:actual_datavalue_count]
                        # save rates in ascending order so small rates are not lost when looking at the cumulative sum
                        keys = list(reversed(keys))
                        destinations[0:len(keys)] = keys
                        rates[0:len(keys)] = [layer[node][key] for key in keys]
                    else:
                        warn(f"No destination nodes found for node {node}", category=UserWarning)
                    destinations.tofile(file)
                    rates.tofile(file)

        return binaryfile

    _MIGRATION_TYPE_LOOKUP = {
        "LOCAL_MIGRATION": LOCAL_MIGRATION,
        "REGIONAL_MIGRATION": REGIONAL_MIGRATION
    }

    _GENDER_DATATYPE_LOOKUP = {
        "SAME_FOR_BOTH_GENDERS": SAME_FOR_BOTH_GENDERS,
        "ONE_FOR_EACH_GENDER": ONE_FOR_EACH_GENDER
    }

    _INTERPOLATION_TYPE_LOOKUP = {
        "LINEAR_INTERPOLATION": LINEAR_INTERPOLATION,
        "PIECEWISE_CONSTANT": PIECEWISE_CONSTANT
    }


def from_file(binaryfile: Path, metafile: Path = None):
    """Reads migration data file from given binary (and associated JSON metadata file)

    Args:
        binaryfile (Path): path to binary file (metadata file is assumed to be at same location with ".json" suffix)
        metafile (Path): use given metafile rather than inferring metafile name from the binary file name

    Returns:
        Migration object representing binary data in the given file.
    """
    binaryfile = Path(binaryfile).absolute()
    metafile = metafile if metafile else binaryfile.parent / (binaryfile.name + ".json")

    if not binaryfile.exists():
        raise RuntimeError(f"Cannot find migration binary file '{binaryfile}'")
    if not metafile.exists():
        raise RuntimeError(f"Cannot find migration metadata file '{metafile}'.")
    with metafile.open("r") as file:
        jason = json.load(file)

    # these are the minimum required entries to load a migration file
    assert _METADATA in jason, f"Metadata file '{metafile}' does not have a 'Metadata' entry."
    metadata = jason[_METADATA]
    assert _NODECOUNT in metadata, f"Metadata file '{metafile}' does not have a 'NodeCount' entry."
    assert _DATAVALUECOUNT in metadata, f"Metadata file '{metafile}' does not have a 'DatavalueCount' entry."
    assert _NODEOFFSETS in jason, f"Metadata file '{metafile}' does not have a 'NodeOffsets' entry."

    migration = VectorMigration()
    migration.Author = _value_with_default(metadata, _AUTHOR, _author())
    migration.DateCreated = _try_parse_date(metadata[_DATECREATED]) if _DATECREATED in metadata else datetime.now()
    migration.Tool = _value_with_default(metadata, _TOOLNAME, _EMODPYMALARIA)
    migration.IdReference = _value_with_default(metadata, _IDREFERENCE, VectorMigration.IDREF_LEGACY)
    migration.MigrationType = VectorMigration._MIGRATION_TYPE_LOOKUP[_value_with_default(metadata,
                                                                                         _MIGRATIONTYPE,
                                                                                         "LOCAL_MIGRATION")]
    migration.GenderDataType = VectorMigration._GENDER_DATATYPE_LOOKUP[_value_with_default(metadata,
                                                                                           _GENDERDATATYPE,
                                                                                           "SAME_FOR_BOTH_GENDERS")]
    migration.AgesYears = _value_with_default(metadata, _AGESYEARS, [])
    migration.InterpolationType = VectorMigration._INTERPOLATION_TYPE_LOOKUP[_value_with_default(metadata,
                                                                                                 _INTERPOLATIONTYPE,
                                                                                                 "PIECEWISE_CONSTANT")]

    node_count = metadata[_NODECOUNT]
    node_offsets = jason[_NODEOFFSETS]
    if len(node_offsets) != 16 * node_count:
        raise RuntimeError(f"Length of node offsets string {len(node_offsets)} != 16 * node count {node_count}.")
    offsets = _parse_node_offsets(node_offsets, node_count)
    datavalue_count = metadata[_DATAVALUECOUNT]
    with binaryfile.open("rb") as file:
        for gender in range(1 if migration.GenderDataType == VectorMigration.SAME_FOR_BOTH_GENDERS else 2):
            for age in migration.AgesYears if migration.AgesYears else [0]:
                layer = migration._layers[migration._index_for_gender_and_age(gender, age)]
                for node, offset in offsets.items():
                    file.seek(offset, SEEK_SET)
                    destinations = np.fromfile(file, dtype=np.uint32, count=datavalue_count)
                    rates = np.fromfile(file, dtype=np.float64, count=datavalue_count)
                    for destination, rate in zip(destinations, rates):
                        if rate > 0:
                            layer[node][destination] = rate

    return migration


def examine_file(filename):
    def name_for_gender_datatype(e: int) -> str:
        return VectorMigration._GENDER_DATATYPE_ENUMS[e] if e in VectorMigration._GENDER_DATATYPE_ENUMS else "unknown"

    def name_for_interpolation(e: int) -> str:
        return VectorMigration._INTERPOLATION_TYPE_ENUMS[
            e] if e in VectorMigration._INTERPOLATION_TYPE_ENUMS else "unknown"

    def name_for_migration_type(e: int) -> str:
        return VectorMigration._MIGRATION_TYPE_ENUMS[e] if e in VectorMigration._MIGRATION_TYPE_ENUMS else "unknown"

    migration = from_file(filename)
    print(f"Author:            {migration.Author}")
    print(f"DatavalueCount:    {migration.DatavalueCount}")
    print(f"DateCreated:       {migration.DateCreated:%a %B %d %Y %H:%M}")
    print(f"IdReference:       {migration.IdReference}")
    print(f"MigrationType:     {migration.MigrationType} ({name_for_migration_type(migration.MigrationType)})")
    print(f"NodeCount:         {migration.NodeCount}")
    print(f"NodeOffsets:       {migration.NodeOffsets}")
    print(f"Tool:              {migration.Tool}")
    print(f"Nodes:             {migration.Nodes}")

    return


def _author() -> str:
    username = ""
    if system() == "Windows":
        username = environ["USERNAME"]
    elif "USER" in environ:
        username = environ["USER"]
    return username


def _parse_node_offsets(string: str, count: int) -> dict:
    assert len(string) == 16 * count, f"Length of node offsets string {len(string)} != 16 * node count {count}."

    offsets = {}
    for index in range(count):
        base = 16 * index
        offset = base + 8
        offsets[int(string[base:base + 8], 16)] = int(string[offset:offset + 8], 16)

    return offsets


def _try_parse_date(string: str) -> datetime:
    patterns = [
        "%a %b %d %Y %H:%M:%S",
        "%a %b %d %H:%M:%S %Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S.%f"
    ]

    for pattern in patterns:
        try:
            timestamp = datetime.strptime(string, pattern)
            return timestamp
        except ValueError:
            pass

    timestamp = datetime.now()
    warn(f"Could not parse date stamp '{string}', using datetime.now() ({timestamp})")

    return timestamp


def _value_with_default(dictionary: dict, key: str, default: object) -> object:
    return dictionary[key] if key in dictionary else default


"""
utility functions emodpy-utils?
"""


def from_params(demographics_file_path: any = None, population: int = 1e6, num_nodes: int = 100,
                migration_factor: float = 1.0, fraction_rural=0.3,
                id_ref="IfReference", migration_type=VectorMigration.LOCAL_MIGRATION):
    """
    This function is for creating a migration file that goes with a (multinode)
    demographics file created from a few parameters, as opposed to one from real-world data.
    Note that the 'demographics_file_path" input param is not used at this time but in future
    will be exploited to ensure nodes, etc., match.
    """
    # ***** Write migration files *****
    # NOTE: This goes straight from input 'data' -- parameters -- to output file.
    # We really want to go from input parameters to standard data representation of migration data
    # and then to file as a separate decoupled step.
    ucellb = np.array([[1.0, 0.0], [-0.5, 0.86603]])
    nlocs = np.random.rand(num_nodes, 2)
    nlocs[0, :] = 0.5
    nlocs = np.round(np.matmul(nlocs, ucellb), 4)
    # Calculate inter-node distances on periodic grid
    nlocs = np.tile(nlocs, (9, 1))
    nlocs[0 * num_nodes:1 * num_nodes, :] += [0.0, 0.0]
    nlocs[1 * num_nodes:2 * num_nodes, :] += [1.0, 0.0]
    nlocs[2 * num_nodes:3 * num_nodes, :] += [-1.0, 0.0]
    nlocs[3 * num_nodes:4 * num_nodes, :] += [0.0, 0.0]
    nlocs[4 * num_nodes:5 * num_nodes, :] += [1.0, 0.0]
    nlocs[5 * num_nodes:6 * num_nodes, :] += [-1.0, 0.0]
    nlocs[6 * num_nodes:7 * num_nodes, :] += [0.0, 0.0]
    nlocs[7 * num_nodes:8 * num_nodes, :] += [1.0, 0.0]
    nlocs[8 * num_nodes:9 * num_nodes, :] += [-1.0, 0.0]
    nlocs[0 * num_nodes:1 * num_nodes, :] += [0.0, 0.0]
    nlocs[1 * num_nodes:2 * num_nodes, :] += [0.0, 0.0]
    nlocs[2 * num_nodes:3 * num_nodes, :] += [0.0, 0.0]
    nlocs[3 * num_nodes:4 * num_nodes, :] += [-0.5, 0.86603]
    nlocs[4 * num_nodes:5 * num_nodes, :] += [-0.5, 0.86603]
    nlocs[5 * num_nodes:6 * num_nodes, :] += [-0.5, 0.86603]
    nlocs[6 * num_nodes:7 * num_nodes, :] += [0.5, -0.86603]
    nlocs[7 * num_nodes:8 * num_nodes, :] += [0.5, -0.86603]
    nlocs[8 * num_nodes:9 * num_nodes, :] += [0.5, -0.86603]
    distgrid = spspd.squareform(spspd.pdist(nlocs))
    nborlist = np.argsort(distgrid, axis=1)
    npops = Demog.get_node_pops_from_params(population, num_nodes, fraction_rural)

    migration = VectorMigration()
    migration.IdReference = id_ref

    for source in range(num_nodes):
        for index in range(1, 31):
            if distgrid.shape[0] > index:
                destination = int(np.mod(nborlist[source, index], num_nodes)) + 1

                tnode = int(np.mod(nborlist[source, index], num_nodes))
                idnode = nborlist[source, index]
                rate = migration_factor * npops[tnode] / np.sum(npops) / distgrid[source, idnode]
            else:
                destination = 0
                rate = 0.0

            migration[source][destination] = rate

    migration.MigrationType = migration_type
    return migration


# def from_demog_and_param_gravity_webservice(demographics_file_path: str, params: str, id_ref: str,
#                                             migration_type=VectorMigration.LOCAL_MIGRATION) -> VectorMigration:
#     """
#     Calls a webservice (running on a GPU) to calculate the migration patterns quickly.
#
#     Args:
#         demographics_file_path: Path to the demographics file.
#         params: Path to the json file with parameters for gravity calculation and server url.
#         id_ref: Metadata tag that needs to match corresponding value in demographics file.
#         migration_type: Migration type.
#
#     Returns:
#         Migration object
#
#     """
#
#     with Path(params).open("r") as f_params:
#         params_url = json.load(f_params)
#
#     # load
#     rates = client.run(Path(demographics_file_path), params_url)
#
#     demog = Demog.from_file(demographics_file_path)
#     migration = VectorMigration()
#     nodes = [node.forced_id for node in demog.nodes]
#
#     # we need a 0-N index for the NumPy array and the node ID for the migration file
#     for i, src in enumerate(nodes):
#         for j, dst in enumerate(nodes):
#             if dst != src:
#                 migration[dst][src] = rates[i, j]
#
#     migration.IdReference = id_ref
#     migration.MigrationType = migration_type
#
#     return migration


# TODO: just use task to reload the demographics files into an object to use for this

def from_demographics_and_gravity_params(demographics_object, gravity_params: list,
                                         filename: str = None):
    """
        This function takes a demographics object, creates a vector migration file based on the populations and
        distances of nodes and saves to be used by the sim

    Args:
        demographics_object: demographics object created by Demographics class (use Demographics.from_file()
            to load a demographics file you already have and pass in the returned object)
        gravity_params: a list of four parameters that will affect the gravity model
            gravity_params[0] denoted as g[0], etc, and they are used in the following way:
            migration_rate = g[0] * (from_node_population^(g[1]-1)) * (to_node_population^g[2]) * (distance^g[3])
            if rate >= 1, 1 is used.
        filename: name of migration file to be created and added to the experiment,
            Default: vector_migration.bin

    Returns:
        VectorMigration object
    """

    def _compute_migration_rate(gravity_params, from_node_population, to_node_population, distance):
        """
        Utility function for computing migration rates using gravity model

        Args:
            gravity_params: a list of four parameters that will affect the gravity model
                gravity_params[0] denoted as g[0], etc, and they are used in the following way:
                migration_rate = g[0] * (from_node_population^(g[1]-1)) * (to_node_population^g[2]) * (distance^g[3])
                if migration_rate >= 1, 1 is used.
            from_node_population: Initial_Population in the from_node
            to_node_population: Initial_Population in the to_node
            distance: distance, in kilomenteres, between two nodes

        Returns:
            Rate of vector migration from from_node to to_node

        """
        # If home/dest node has 0 pop, assume this node is the regional work node-- no local migration allowed
        if from_node_population == 0 or to_node_population == 0:
            return 0
        else:
            migration_rate = gravity_params[0] * (from_node_population ** (gravity_params[1] - 1)) \
                             * (to_node_population ** gravity_params[2]) * (distance ** gravity_params[3])
            final_rate = np.min([1., migration_rate])
            return final_rate

    def _compute_migration_dict(node_list: list, gravity_params: list, exclude_nodes: list = None):
        """
        Utility function for computing migration value map.

        Args:
            node_list: list of nodes as dictionaries created from the demographics object
            gravity_params: a list of four parameters that will affect the gravity model
                gravity_params[0] denoted as g[0], etc, and they are used in the following way:
                rate = g[0] * (from_node_population^(g[1]-1)) * (to_node_population^g[2]) * (distance^g[3])
                if rate >= 1, 1 is used.
            exclude_nodes: a list of node ids for nodes you don't want any migration happening to or from.

        Returns:
            VectorMigration object based on demographics object that was passed in
        """
        excluded_nodes = set(exclude_nodes) if exclude_nodes else set()
        v_migration = VectorMigration()
        geodesic = Geodesic.WGS84

        for source_node in node_list:
            source_id = source_node["NodeID"]
            src_lat = source_node["NodeAttributes"]["Latitude"]
            src_long = source_node["NodeAttributes"]["Longitude"]
            src_pop = source_node["NodeAttributes"]["InitialPopulation"]

            if source_id in excluded_nodes:
                continue
            for destination_node in node_list:
                if destination_node == source_node:
                    continue
                dest_id = destination_node["NodeID"]
                if dest_id in excluded_nodes:
                    continue
                dst_lat = destination_node["NodeAttributes"]["Latitude"]
                dst_long = destination_node["NodeAttributes"]["Longitude"]
                dst_pop = destination_node["NodeAttributes"]["InitialPopulation"]

                distance = geodesic.Inverse(src_lat, src_long, dst_lat, dst_long, Geodesic.DISTANCE)['s12'] / 1000  # km
                rate = _compute_migration_rate(gravity_params, src_pop, dst_pop, distance)
                v_migration[source_id][dest_id] = rate

        return v_migration

    nodes = [node.to_dict() for node in demographics_object.nodes]
    v_migration = _compute_migration_dict(nodes, gravity_params)
    v_migration.IdReference = demographics_object.idref
    v_migration.MigrationType = "LOCAL_MIGRATION"
    # save migration object to file
    if not filename:
        filename = f"vector_migration.bin"
    v_migration.to_file(Path(filename))

# by gender, by age
_mapping_fns = {
    (False, False): lambda m, i, g, a: m[i],
    (False, True): lambda m, i, g, a: m[i:a],
    (True, False): lambda m, i, g, a: m[i:g],
    (True, True): lambda m, i, g, a: m[i:g:a]
}

# by gender, by age
_display_fns = {
    (False, False): lambda i, g, a, d, r: f"{i},{d},{r}",  # id only
    (False, True): lambda i, g, a, d, r: f"{i},{a},{d},{r}",  # id:age
    (True, False): lambda i, g, a, d, r: f"{i},{g},{d},{r}",  # id:gender
    (True, True): lambda i, g, a, d, r: f"{i},{g},{a},{d},{r}"  # id:gender:age
}


def to_csv():
    mapping = _mapping_fns[(migration.GenderDataType == VectorMigration.ONE_FOR_EACH_GENDER, bool(migration.AgesYears))]
    display = _display_fns[(migration.GenderDataType == VectorMigration.ONE_FOR_EACH_GENDER, bool(migration.AgesYears))]

    print(display("from_node", "to_node", "rate"))
    for gender in range(1 if migration.GenderDataType == VectorMigration.SAME_FOR_BOTH_GENDERS else 2):
        for age in migration.AgesYears if migration.AgesYears else [0]:
            for node in migration.Nodes:
                for destination, rate in mapping(migration, node, gender, age).items():
                    print(display(node, gender, age, destination, rate))


def from_csv(filename_path: str, id_reference: str, migration_type: str = "LOCAL_MIGRATION",
             author: str = None):
    """
    Create migration from csv file. The file should have columns 'from_node' for the node ids from which vector is
    migrating, 'to_node' for the node ids that the vector is migrating to, and 'rate' for the migration rate.

    Example::

            from_node,to_node,rate
            1, 4, 0.5
            4, 1, 0.01

    Args:
        filename_path: name (if same folder) or path+name of the csv file
        id_reference: IdReference parameter to set for the migration file, it needs to be the same as
            IdReference parameter in your demographics files.
        migration_type: "LOCAL_MIGRATION" or "REGIONAL_MIGRATION" setting, "LOCAL_MIGRATION" can have 8 "to_nodes"
            while "REGIONAL_MIGRATION" can have 30, default is "LOCAL_MIGRATION"
        author: optional metadata of who is the author(you) of the migration file, default - your username or empty
            string will be used

    Returns:
        Migration object to be manipulated or written out as a file using to_file() function

    """
    migration = VectorMigration()
    migration.IdReference = id_reference
    migration._migrationtype = VectorMigration._MIGRATION_TYPE_LOOKUP[migration_type]
    if author:
        migration.Author = author
    with Path(filename_path).open("r") as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data_read = False
        for row in reader:
            csv_data_read = True
            migration[int(row['from_node'])][int(row['to_node'])] = float(row['rate'])
        assert csv_data_read, "Please make sure you have column headers of 'from_node', 'to_node', 'rate' in your file.\n"

    return migration
