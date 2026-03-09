# Malaria Example Scenario

## (Windows) Environment Prep
- Open a terminal/shell/console.
- Create virtual environment (python -m venv emodpy)
- Activate virtual environment (emodpy\Scripts\activate)
- Edit your pip.conf (or pip.ini) to make sure it's pointing at our Artifactory.
NOTE: If you do not have a pip.ini (Windows) or pip.conf (Linux) then create a new one in your home directory.
```
[global]
index-url = https://packages.idmod.org/api/pypi/pypi-production/simple
```

## Alternate (Docker-based Linux) Environment Prep
- TBD... 

## BOTH
- Make sure you are VPN-ed in or otherwise 'inside the building'.
  ###### Why? This is currently needed for access to Bamboo for the EMOD/DTK executable and matching schema.

## Installation
```
pip install emodpy_malaria
pip install dataclasses
pip install keyrings.alt (Linux only)
git clone https://github.com/InstituteforDiseaseModeling/emodpy-malaria.git
cd emodpy-malaria/examples/start_here
```

## Configuration
Open and edit manifest.py and create folders like "Assets" and "download". You are expected to choose where you are telling the system to look. 

## Run
```
python example.py
```pip
(Enter necessary creds as prompted; include '@idmod.org' for bamboo. If the program seems to hang at the beginning, check that you are VPN'ed.)

## Study
Observe results on COMPS(2)
