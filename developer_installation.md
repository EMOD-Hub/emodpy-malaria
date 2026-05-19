# Developer installation

First, fork and clone the repository, then navigate into it:

```
git clone https://github.com/EMOD-Hub/emodpy-malaria.git
cd emodpy-malaria
```

**Option 1** — editable install (changes take effect immediately):

```
pip install -e .
```

**Option 2** — build a wheel (required if testing packaging):

```
pip install build
python -m build
pip install dist\emodpy_malaria-XXXX.whl
```
