# Malaria Example Scenario

## (Windows) Environment Prep
- Open a terminal/shell/console.
- Create virtual environment (python -m venv emodpy)
- Activate virtual environment (emodpy\Scripts\activate)

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
git clone https://github.com/EMOD-Hub/emodpy-malaria.git
cd emodpy-malaria/examples-container/campaign_sweep/
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
