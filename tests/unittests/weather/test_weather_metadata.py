import json
import shutil
import tempfile
import unittest

from datetime import datetime
from pathlib import Path

from emodpy_malaria.weather.weather_metadata import WeatherMetadata, WeatherAttributes
from emodpy_malaria.weather.weather_metadata import _META_ID_REFERENCE


class WeatherMetadataTests(unittest.TestCase):
    max_uint32 = int("FFFFFFFF", 16)

    def setUp(self) -> None:
        self.current_dir = Path(__file__).parent
        dtk_file_path = 'case_default_names/dtk_15arcmin_air_temperature_daily.bin.json'
        self.case_dtk_file = self.current_dir.joinpath(dtk_file_path)
        self.test_dir = tempfile.mkdtemp(suffix="emodpy_malaria_unittests")
        self.test_file = Path(self.test_dir).joinpath("new_file.bin.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_attributes_only_defaults(self):
        wa = WeatherAttributes()
        self.assertEqual(wa.id_reference, "Default")
        self.assertEqual(wa.spatial_resolution, "Unspecified")
        self.assertEqual(wa.tool, "emodpy_malaria")

    def test_attributes_from_dict(self):
        value1 = "My custom ref"
        value2 = "123"

        wa = WeatherAttributes({_META_ID_REFERENCE: value1})
        self.assertEqual(wa.id_reference, value1)
        wa.id_reference = value2
        self.assertEqual(wa.id_reference, value2)

    def test_attributes_from_custom(self):
        custom_name = "CustomAttribute"
        custom_value1 = "My custom attribute"

        wa = WeatherAttributes({custom_name: custom_value1})
        self.assertIn(custom_name, wa.attributes_dict)
        self.assertEqual(wa.attributes_dict[custom_name], custom_value1)

    def test_metadata_read(self):
        wm: WeatherMetadata = WeatherMetadata.from_file(self.case_dtk_file)
        expected_meta, expected_offset = read_metafile(self.case_dtk_file)
        self.assertEqual(expected_meta['Author'], wm.author)
        self.assertEqual(expected_offset, wm.node_offset_str)

    def test_metadata_create(self):
        wm: WeatherMetadata = WeatherMetadata(
            node_ids=[1, 2, 3],
            series_len=3,
            attributes=WeatherAttributes(
                start_year=2001,
                end_year=2010,
                provenance="Weather unittest file.",
                lat_max=20.1,
                lat_min=19.2,
                lon_max=120.01,
                lon_min=130.02))

        expected_offset_str = "0000000100000000000000020000000c0000000300000018"
        self.assertEqual(wm.node_offset_str, expected_offset_str)

        wm.to_file(self.test_file)
        meta, offset = read_metafile(self.test_file)
        self.assertEqual(offset, expected_offset_str)

    def test_metadata_node_id_range(self):
        for node_id in [1, self.max_uint32]:
            wm: WeatherMetadata = WeatherMetadata(node_ids=[node_id], series_len=3)
            self.assertEqual(wm.nodes, [node_id])

        for node_id in [0, self.max_uint32 + 1]:
            with self.assertRaises(ValueError):
                wm: WeatherMetadata = WeatherMetadata(node_ids=[node_id], series_len=3)

    def test_metadata_offset_range(self):
        for offset in [0, self.max_uint32]:
            wm: WeatherMetadata = WeatherMetadata(node_ids={1: offset}, series_len=3)
            self.assertEqual(list(wm.node_offsets.values())[0], offset)

        for offset in [-1, self.max_uint32 + 1]:
            with self.assertRaises(ValueError):
                wm: WeatherMetadata = WeatherMetadata(node_ids={1: offset}, series_len=3)

    def test_metadata_create_new_from_existing_node_list(self):
        wm1: WeatherMetadata = WeatherMetadata.from_file(self.case_dtk_file)
        wm2: WeatherMetadata = WeatherMetadata(series_len=wm1.datavalue_count,
                                               node_ids=list(wm1.node_offsets)[:2],
                                               attributes=wm1.attributes)
        wm2.to_file(self.test_file)

        expected_meta, _ = read_metafile(self.test_file)
        expected_offset_str = "6156225a000000006157225800001120"

        self.assertNotEqual(wm1, wm2)   # not equal because in wm2 each node has different offset
        self.assertEqual(wm1.author, expected_meta["Author"])
        self.assertEqual(expected_offset_str, wm2.node_offset_str)

    def test_metadata_required_defaults(self):
        required = WeatherMetadata.required_metadata_defaults_dict()
        required2 = WeatherMetadata.required_metadata_defaults_dict(exclude_keys=list(required))
        self.assertEqual(required["IdReference"], "Default")
        self.assertNotIn("IdReference", required2)

    def test_metadata_create_from_node_list_no_id_reference(self):
        node_ids = [i + 100 for i in list(range(1, 11, 1))]
        wm = WeatherMetadata(node_ids=node_ids, series_len=10, attributes={'No_IdReference': 'Not needed'})
        self.assertIn("IdReference", wm.attributes_dict)

    def test_metadata_edit(self):
        wm1: WeatherMetadata = WeatherMetadata.from_file(self.case_dtk_file)

        shutil.copy2(self.case_dtk_file, self.test_file)
        wm2: WeatherMetadata = WeatherMetadata.from_file(self.test_file)
        new_date = WeatherMetadata.format_create_date(datetime.now())
        wm2.date_created = new_date
        wm2.tool += "-X"
        wm2.author += "-X"
        wm2.id_reference += "-X"
        wm2.update_resolution += "-X"
        wm2.data_years = f"{wm2.data_years[:-1]}9"
        wm2.provenance += "-X"
        wm2.spatial_resolution += "-X"

        wm2.to_file(self.test_file)

        self.assertEqual(f"{wm1.tool}-X", wm2.tool)
        self.assertEqual(str(new_date), wm2.date_created)
        self.assertEqual(f"{wm1.author}-X", wm2.author)
        self.assertEqual(f"{wm1.id_reference}-X", wm2.id_reference)
        self.assertEqual(f"{wm1.update_resolution}-X", wm2.update_resolution)
        self.assertEqual(f"{wm1.data_years[:-1]}9", wm2.data_years)
        self.assertEqual(f"{wm1.provenance}-X", wm2.provenance)
        self.assertEqual(f"{wm1.spatial_resolution}-X", wm2.spatial_resolution)

        self.assertEqual(wm1.node_offset_str, wm2.node_offset_str)


def read_metafile(path):
    content = json.loads(Path(path).read_text())
    meta = content['Metadata']
    offset = content['NodeOffsets']
    return meta, offset


if __name__ == '__main__':
    unittest.main()
