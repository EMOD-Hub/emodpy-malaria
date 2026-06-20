import os
import pathlib

import emod_malaria.bootstrap as dtk

current_directory = pathlib.Path(__file__).resolve().parent
_stash_dir = current_directory / "stash"

_cwd_before = os.getcwd()
dtk.setup(str(_stash_dir))
os.chdir(_cwd_before)

schema_file = str(_stash_dir / "schema.json")
schema_path = schema_file
eradication_path = str(_stash_dir / "Eradication")
