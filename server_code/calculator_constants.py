"""Holds constants related to the Heat Pump Calculator API.  Needed
to separate these from the 'calculator' module due to circular import
issues.
"""
import anvil.server

CALCULATOR_API_BASE_URL = "https://heatpump-api.energytools.com/"

# Map Calculator API Fuel ID to labels and units
FUEL_INFO = {
  "oil1": ('Oil', 'gallons', ',.0f'),
  "propane": ('Propane', 'gallons', ',.0f'),
  "elec": ('Electricity', 'kWh', ',.0f'),
  "birch": ('Birch', 'cords', ',.2f'),
  "spruce": ('Spruce', 'cords', ',.2f'),
  "pellets": ('Wood Pellets', 'pounds', ',.0f'),
  "ng": ('Natural Gas', 'CCF', ',.0f'),
}

# Map End Use IDs to labels
END_USE_LABELS = {
  'space_htg': 'Space Heating',
  'dhw': 'Domestic Hot Water',
  'cooking': 'Cooking',
  'drying': 'Clothes Drying',
  'misc_elec': 'Miscellaneous Electric',
  'ev_charging': 'EV Charging',
  'pv_solar': 'PV Solar',
}

# Pairs the fuel price override input name with the fuel ID
FUEL_NAME_TO_ID = (
  ('oil_price', 'oil1'), 
  ('propane_price', 'propane'), 
  ('ng_price', 'ng'), 
  ('birch_price', 'birch'), 
  ('spruce_price', 'spruce'), 
  ('pellet_price', 'pellets')
)

@anvil.server.callable
def calculator_api_base_url():
  return CALCULATOR_API_BASE_URL
