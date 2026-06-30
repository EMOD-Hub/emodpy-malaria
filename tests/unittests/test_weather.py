import numpy as np
import pandas as pd
import pytest

from emod_api.demographics.node import Node

from emodpy_malaria.demographics.malaria_demographics import MalariaDemographics
from emodpy_malaria.weather.weather_variable import WeatherVariable
from emodpy_malaria.weather.weather_metadata import WeatherAttributes, WeatherMetadata
from emodpy_malaria.weather.weather_data import WeatherData, DataFrameInfo
from emodpy_malaria.weather.weather_set import WeatherSet
from emodpy_malaria.weather import csv_to_weather, weather_to_csv
from emodpy_malaria.weather.weather_config import set_climate_constant, set_climate_by_data
from emodpy_malaria.utils.emod_enum import ClimateUpdateResolution


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_node_series(n_nodes=3, series_len=10):
    """Create synthetic node time series data."""
    return {
        i + 1: np.random.default_rng(seed=i).random(series_len).astype(np.float32)
        for i in range(n_nodes)
    }


def _make_weather_csv_df(n_nodes=2, series_len=5):
    """Create a DataFrame with the 3 weather columns used by EMOD malaria."""
    rng = np.random.default_rng(42)
    rows = []
    for node in range(1, n_nodes + 1):
        for step in range(1, series_len + 1):
            rows.append({
                "nodes": node,
                "steps": step,
                "airtemp": rng.random() * 30 + 10,
                "humidity": rng.random(),
                "rainfall": rng.random() * 0.05,
            })
    return pd.DataFrame(rows)


class MockConfig:
    """Minimal mock of the EMOD config object."""
    class _Params:
        def __setattr__(self, key, value):
            self.__dict__[key] = value

        def __getattr__(self, key):
            return self.__dict__.get(key)

    def __init__(self):
        self.parameters = self._Params()


# ---------------------------------------------------------------------------
# WeatherVariable
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWeatherVariable:
    def test_list_all(self):
        all_vars = WeatherVariable.list()
        assert len(all_vars) == 4
        assert WeatherVariable.AIR_TEMPERATURE in all_vars

    def test_list_exclude(self):
        reduced = WeatherVariable.list(exclude=WeatherVariable.RAINFALL)
        assert len(reduced) == 3
        assert WeatherVariable.RAINFALL not in reduced

    def test_list_exclude_list(self):
        reduced = WeatherVariable.list(exclude=[WeatherVariable.RAINFALL, WeatherVariable.LAND_TEMPERATURE])
        assert len(reduced) == 2

    def test_validate_types_valid(self):
        d = {WeatherVariable.AIR_TEMPERATURE: "temp_col"}
        WeatherVariable.validate_types(d, [str])

    def test_validate_types_none_ok(self):
        WeatherVariable.validate_types(None)

    def test_validate_types_bad_key(self):
        with pytest.raises(TypeError):
            WeatherVariable.validate_types({"bad_key": "value"}, [str])

    def test_validate_types_bad_value_type(self):
        with pytest.raises(TypeError):
            WeatherVariable.validate_types({WeatherVariable.AIR_TEMPERATURE: 123}, [str])


# ---------------------------------------------------------------------------
# WeatherMetadata
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWeatherMetadata:
    def test_from_node_list(self):
        wm = WeatherMetadata(node_ids=[1, 2, 3], series_len=10)
        assert wm.node_count == 3
        assert wm.series_len == 10
        assert wm.series_count == 3
        assert wm.nodes == [1, 2, 3]

    def test_from_offset_dict(self):
        offsets = {1: 0, 2: 40, 3: 0}  # nodes 1 and 3 share data
        wm = WeatherMetadata(node_ids=offsets, series_len=10)
        assert wm.node_count == 3
        assert wm.series_count == 2  # 2 unique offsets

    def test_offset_string_roundtrip(self):
        wm = WeatherMetadata(node_ids=[1, 2], series_len=5)
        offset_str = wm.node_offset_str
        recovered = WeatherMetadata._convert_offset_str_to_dict(offset_str)
        assert recovered == wm.node_offsets

    def test_file_roundtrip(self, tmp_path):
        wm = WeatherMetadata(node_ids=[1, 2, 3], series_len=365)
        path = tmp_path / "test.bin.json"
        wm.to_file(path)
        wm2 = WeatherMetadata.from_file(path)
        assert wm == wm2

    def test_invalid_series_len(self):
        with pytest.raises(ValueError):
            WeatherMetadata(node_ids=[1], series_len=0)

    def test_invalid_node_id(self):
        with pytest.raises(ValueError):
            WeatherMetadata(node_ids=[0], series_len=10)

    def test_to_base_metadata(self):
        wm = WeatherMetadata(node_ids=[1, 2, 3], series_len=10)
        base = wm.to_base_metadata()
        assert base.node_count == 3
        assert base.datavalue_count == 10
        assert sorted(base.node_ids) == [1, 2, 3]


# ---------------------------------------------------------------------------
# WeatherAttributes
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWeatherAttributes:
    def test_defaults(self):
        wa = WeatherAttributes()
        assert wa.id_reference == "Default"
        assert wa.tool == "emodpy_malaria"
        assert wa.author == "Institute for Disease Modeling"

    def test_custom_reference(self):
        wa = WeatherAttributes(reference="Custom")
        assert wa.id_reference == "Custom"

    def test_years(self):
        wa = WeatherAttributes(start_year=2010, end_year=2020)
        assert wa.data_years == "2010-2020"

    def test_equality(self):
        wa1 = WeatherAttributes(reference="A")
        wa2 = WeatherAttributes(reference="A")
        assert wa1 == wa2


# ---------------------------------------------------------------------------
# WeatherData
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWeatherData:
    def test_from_dict_basic(self):
        ns = _make_node_series(3, 10)
        wd = WeatherData.from_dict(ns)
        assert wd.metadata.node_count == 3
        assert wd.metadata.series_len == 10
        assert wd.data.shape[1] == 10

    def test_from_dict_duplicate_optimization(self):
        shared = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        ns = {1: shared, 2: shared, 3: np.array([4.0, 5.0, 6.0], dtype=np.float32)}
        wd = WeatherData.from_dict(ns)
        assert wd.metadata.series_count == 2  # only 2 unique series stored
        assert wd.metadata.node_count == 3

    def test_from_dict_nan_rejected(self):
        ns = {1: [1.0, float("nan"), 3.0]}
        with pytest.raises(ValueError, match="NaN"):
            WeatherData.from_dict(ns)

    def test_from_dict_inf_rejected(self):
        ns = {1: [1.0, float("inf"), 3.0]}
        with pytest.raises(ValueError, match="infinite"):
            WeatherData.from_dict(ns)

    def test_to_dict_roundtrip(self):
        ns = _make_node_series(2, 5)
        wd = WeatherData.from_dict(ns)
        recovered = wd.to_dict()
        for node_id in ns:
            np.testing.assert_array_almost_equal(recovered[node_id], ns[node_id])

    def test_file_roundtrip(self, tmp_path):
        ns = _make_node_series(3, 30)
        wd = WeatherData.from_dict(ns)
        path = tmp_path / "test_weather.bin"
        wd.to_file(path)
        wd2 = WeatherData.from_file(path)
        assert wd == wd2

    def test_from_dataframe(self):
        df = pd.DataFrame({
            "nodes": [1, 1, 1, 2, 2, 2],
            "steps": [1, 2, 3, 1, 2, 3],
            "values": [10.0, 11.0, 12.0, 20.0, 21.0, 22.0],
        })
        wd = WeatherData.from_dataframe(df)
        assert wd.metadata.node_count == 2
        assert wd.metadata.series_len == 3

    def test_to_dataframe(self):
        ns = {1: [10.0, 11.0], 2: [20.0, 21.0]}
        wd = WeatherData.from_dict(ns)
        df = wd.to_dataframe()
        assert len(df) == 4  # 2 nodes * 2 steps
        assert "nodes" in df.columns

    def test_csv_roundtrip(self, tmp_path):
        ns = _make_node_series(2, 5)
        wd = WeatherData.from_dict(ns)
        csv_path = tmp_path / "weather.csv"
        wd.to_csv(csv_path)
        wd2 = WeatherData.from_csv(csv_path)
        for node_id in ns:
            np.testing.assert_array_almost_equal(
                wd2.to_dict()[node_id], ns[node_id]
            )

    def test_empty_dict_rejected(self):
        with pytest.raises(ValueError):
            WeatherData.from_dict({})

    def test_to_base_weather(self):
        ns = _make_node_series(3, 10)
        wd = WeatherData.from_dict(ns)
        base = wd.to_base_weather()
        assert base.node_count == 3
        assert base.datavalue_count == 10
        for node_id in ns:
            np.testing.assert_array_almost_equal(base.nodes[node_id].data, ns[node_id])

    def test_from_base_weather(self):
        from emod_api.weather.weather import Weather as BaseWeather
        base = BaseWeather(node_ids=[1, 2], datavalue_count=5)
        base.nodes[1][:] = [1.0, 2.0, 3.0, 4.0, 5.0]
        base.nodes[2][:] = [6.0, 7.0, 8.0, 9.0, 10.0]
        wd = WeatherData.from_base_weather(base)
        assert wd.metadata.node_count == 2
        assert wd.metadata.series_len == 5
        np.testing.assert_array_almost_equal(wd.to_dict()[1], [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_base_weather_roundtrip(self):
        ns = _make_node_series(2, 5)
        wd = WeatherData.from_dict(ns)
        base = wd.to_base_weather()
        wd2 = WeatherData.from_base_weather(base)
        for node_id in ns:
            np.testing.assert_array_almost_equal(wd2.to_dict()[node_id], ns[node_id])


# ---------------------------------------------------------------------------
# DataFrameInfo
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDataFrameInfo:
    def test_defaults(self):
        info = DataFrameInfo()
        assert info.node_column == "nodes"
        assert info.step_column == "steps"
        assert info.value_column == "values"

    def test_custom_columns(self):
        info = DataFrameInfo(node_column="id", step_column="time", value_column="temp")
        assert info.node_column == "id"

    def test_detect_columns(self):
        df = pd.DataFrame({"node": [1], "step": [1], "value": [10.0]})
        info = DataFrameInfo.detect_columns(df)
        assert info.node_column == "node"
        assert info.step_column == "step"
        assert info.value_column == "value"

    def test_detect_columns_missing(self):
        df = pd.DataFrame({"x": [1], "y": [1], "z": [10.0]})
        with pytest.raises(NameError):
            DataFrameInfo.detect_columns(df)


# ---------------------------------------------------------------------------
# WeatherSet
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWeatherSet:
    def test_from_dataframe_roundtrip(self, tmp_path):
        df = _make_weather_csv_df(n_nodes=2, series_len=5)
        ws = WeatherSet.from_dataframe(df)
        assert len(ws) == 3
        assert WeatherVariable.AIR_TEMPERATURE in ws.weather_variables
        assert WeatherVariable.LAND_TEMPERATURE not in ws.weather_variables

        df2 = ws.to_dataframe()
        assert len(df2) == len(df)

    def test_file_roundtrip(self, tmp_path):
        df = _make_weather_csv_df(n_nodes=2, series_len=5)
        ws = WeatherSet.from_dataframe(df)
        ws.to_files(dir_path=tmp_path)

        ws2 = WeatherSet.from_files(dir_path=tmp_path)
        assert len(ws2) == 3

        for v in ws.weather_variables:
            d1 = ws[v].to_dict()
            d2 = ws2[v].to_dict()
            for node_id in d1:
                np.testing.assert_array_almost_equal(d1[node_id], d2[node_id])

    def test_csv_roundtrip(self, tmp_path):
        df = _make_weather_csv_df(n_nodes=2, series_len=5)
        ws = WeatherSet.from_dataframe(df)
        csv_path = tmp_path / "all_weather.csv"
        ws.to_csv(csv_path)

        ws2 = WeatherSet.from_csv(csv_path)
        assert len(ws2) == 3

    def test_make_file_paths(self):
        paths = WeatherSet.make_file_paths()
        assert len(paths) == 3
        for v, p in paths.items():
            assert p.endswith(".bin")

    def test_select_weather_files_empty(self, tmp_path):
        result = WeatherSet.select_weather_files(dir_path=tmp_path)
        assert len(result) == 0

    def test_notes_stored_in_metadata(self, tmp_path):
        df = _make_weather_csv_df(n_nodes=2, series_len=5)
        ws = WeatherSet.from_dataframe(df, notes="ERA5 reanalysis, bilinear interpolation to nodes")
        assert ws.notes == "ERA5 reanalysis, bilinear interpolation to nodes"

        ws.to_files(dir_path=tmp_path)
        ws2 = WeatherSet.from_files(dir_path=tmp_path)
        assert ws2.notes == "ERA5 reanalysis, bilinear interpolation to nodes"


# ---------------------------------------------------------------------------
# Top-level convenience functions
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConvenienceFunctions:
    def test_csv_to_weather_from_dataframe(self, tmp_path):
        df = _make_weather_csv_df(n_nodes=2, series_len=5)
        ws = csv_to_weather(df, weather_dir=tmp_path)
        assert len(ws) == 3

        bin_files = list(tmp_path.glob("*.bin"))
        json_files = list(tmp_path.glob("*.bin.json"))
        assert len(bin_files) == 3
        assert len(json_files) == 3

    def test_weather_to_csv_roundtrip(self, tmp_path):
        df_in = _make_weather_csv_df(n_nodes=2, series_len=5)
        csv_to_weather(df_in, weather_dir=tmp_path)

        df_out, attrs = weather_to_csv(weather_dir=tmp_path)
        assert isinstance(df_out, pd.DataFrame)
        assert isinstance(attrs, WeatherAttributes)
        assert len(df_out) == len(df_in)


# ---------------------------------------------------------------------------
# Climate config helpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestClimateConfig:
    def test_set_climate_constant(self):
        config = MockConfig()
        set_climate_constant(config, air_temperature=25, rainfall=5)
        assert str(config.parameters.Climate_Model) == "CLIMATE_CONSTANT"
        assert config.parameters.Base_Air_Temperature == 25
        assert config.parameters.Base_Rainfall == 5
        assert config.parameters.Enable_Climate_Stochasticity == 0

    def test_set_climate_constant_auto_stochastic_from_temp_variance(self):
        config = MockConfig()
        set_climate_constant(config, air_temperature_variance=2.0)
        assert config.parameters.Enable_Climate_Stochasticity == 1
        assert config.parameters.Air_Temperature_Variance == 2.0

    def test_set_climate_constant_auto_stochastic_from_humidity_variance(self):
        config = MockConfig()
        set_climate_constant(config, relative_humidity_variance=0.05)
        assert config.parameters.Enable_Climate_Stochasticity == 1
        assert config.parameters.Relative_Humidity_Variance == 0.05

    def test_set_climate_constant_auto_stochastic_from_rainfall(self):
        config = MockConfig()
        set_climate_constant(config, enable_rainfall_stochasticity=True)
        assert config.parameters.Enable_Climate_Stochasticity == 1
        assert config.parameters.Enable_Rainfall_Stochasticity == 1

    def test_set_climate_constant_no_stochastic_by_default(self):
        config = MockConfig()
        set_climate_constant(config)
        assert config.parameters.Enable_Climate_Stochasticity == 0

    def test_set_climate_by_data(self):
        config = MockConfig()
        set_climate_by_data(
            config,
            air_temperature_filename="air.bin",
            rainfall_filename="rain.bin",
            relative_humidity_filename="humid.bin",
        )
        assert str(config.parameters.Climate_Model) == "CLIMATE_BY_DATA"
        assert config.parameters.Air_Temperature_Filename == "air.bin"
        assert config.parameters.Land_Temperature_Filename == "air.bin"
        assert config.parameters.Land_Temperature_Offset == 0.0
        assert config.parameters.Rainfall_Scale_Factor == 1.0

    def test_set_climate_by_data_with_offsets(self):
        config = MockConfig()
        set_climate_by_data(
            config,
            air_temperature_filename="a.bin",
            rainfall_filename="r.bin",
            relative_humidity_filename="h.bin",
            air_temperature_offset=2.5,
            rainfall_scale_factor=0.8,
        )
        assert config.parameters.Air_Temperature_Offset == 2.5
        assert config.parameters.Rainfall_Scale_Factor == 0.8

    def test_set_climate_constant_land_temp_equals_air(self):
        config = MockConfig()
        set_climate_constant(config, air_temperature=25)
        assert config.parameters.Base_Land_Temperature == 25

    def test_set_climate_constant_bad_resolution(self):
        config = MockConfig()
        with pytest.raises(ValueError, match="update_resolution"):
            set_climate_constant(config, update_resolution="INVALID")

    def test_set_climate_by_data_string_resolution(self):
        config = MockConfig()
        set_climate_by_data(
            config,
            air_temperature_filename="a.bin",
            rainfall_filename="r.bin",
            relative_humidity_filename="h.bin",
            update_resolution="CLIMATE_UPDATE_MONTH",
        )
        assert str(config.parameters.Climate_Update_Resolution) == "CLIMATE_UPDATE_MONTH"


# ---------------------------------------------------------------------------
# Demographics.add_weather integration
# ---------------------------------------------------------------------------

def _make_demog(node_ids):
    """Create a MalariaDemographics with the given node IDs."""
    nodes = [Node(lat=0, lon=0, pop=1000, forced_id=nid) for nid in node_ids]
    return MalariaDemographics(nodes=nodes, idref="test_idref")


def _make_weather_set(node_ids, series_len=5):
    """Create a WeatherSet with the given node IDs."""
    rng = np.random.default_rng(42)
    rows = []
    for node in node_ids:
        for step in range(1, series_len + 1):
            rows.append({
                "nodes": node,
                "steps": step,
                "airtemp": rng.random() * 30 + 10,
                "humidity": rng.random(),
                "rainfall": rng.random() * 0.05,
            })
    df = pd.DataFrame(rows)
    return WeatherSet.from_dataframe(df)


@pytest.mark.unit
class TestAddWeather:
    def test_add_weather_basic(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2])
        demog.add_weather(ws)

        assert len(demog.migration_files) == 3
        assert len(demog.implicits) > 0

        bin_files = list(tmp_path.glob("*.bin"))
        json_files = list(tmp_path.glob("*.bin.json"))
        assert len(bin_files) == 3
        assert len(json_files) == 3

    def test_add_weather_sets_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2])
        demog.add_weather(
            ws,
            air_temperature_offset=2.5,
            rainfall_scale_factor=0.8,
        )

        config = MockConfig()
        for fn in demog.implicits:
            config = fn(config)

        assert str(config.parameters.Climate_Model) == "CLIMATE_BY_DATA"
        assert config.parameters.Air_Temperature_Offset == 2.5
        assert config.parameters.Rainfall_Scale_Factor == 0.8
        assert config.parameters.Air_Temperature_Filename is not None
        assert config.parameters.Land_Temperature_Filename == config.parameters.Air_Temperature_Filename
        assert config.parameters.Land_Temperature_Offset == 0.0

    def test_add_weather_daily_filenames(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2])
        demog.add_weather(ws)

        names = [p.name for p in demog.migration_files]
        assert "airtemp_daily.bin" in names
        assert "rainfall_daily.bin" in names
        assert "humidity_daily.bin" in names

    def test_add_weather_monthly_filenames(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2])
        demog.add_weather(ws, update_resolution=ClimateUpdateResolution.CLIMATE_UPDATE_MONTH)

        names = [p.name for p in demog.migration_files]
        assert "airtemp_monthly.bin" in names
        assert "rainfall_monthly.bin" in names
        assert "humidity_monthly.bin" in names

    def test_add_weather_prefix_filenames(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2])
        demog.add_weather(ws, prefix="era5_")

        names = [p.name for p in demog.migration_files]
        assert "era5_airtemp_daily.bin" in names
        assert "era5_rainfall_daily.bin" in names
        assert "era5_humidity_daily.bin" in names

    def test_add_weather_extra_nodes(self):
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2, 3])
        with pytest.raises(ValueError, match="extra nodes"):
            demog.add_weather(ws)

    def test_add_weather_missing_nodes(self):
        demog = _make_demog([1, 2, 3])
        ws = _make_weather_set([1, 2])
        with pytest.raises(ValueError, match="missing nodes"):
            demog.add_weather(ws)

    def test_add_weather_stamps_demog_idref(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2])
        assert ws.id_reference != "test_idref"
        demog.add_weather(ws)
        assert ws.id_reference == "test_idref"

    def test_add_weather_rejects_non_weatherset(self):
        demog = _make_demog([1])
        with pytest.raises(TypeError, match="WeatherSet"):
            demog.add_weather("not_a_weather_set")

    def test_add_weather_rejects_string_update_resolution(self):
        demog = _make_demog([1, 2])
        ws = _make_weather_set([1, 2])
        with pytest.raises(TypeError, match="ClimateUpdateResolution"):
            demog.add_weather(ws, update_resolution="CLIMATE_UPDATE_DAY")
