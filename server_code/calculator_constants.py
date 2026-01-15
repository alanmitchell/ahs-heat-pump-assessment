"""Holds constants related to the Heat Pump Calculator API.  Needed
to separate these from the 'calculator' module due to circular import
issues.
"""
import anvil.server

CALCULATOR_API_BASE_URL = "https://heatpump-api.energytools.com/"

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
