"""Module for managing the interface to the backend Calculator API.
"""
import anvil.server
import anvil.http

# Base URL to access heat pump calculator API endpoints.
CALCULATOR_API_BASE_URL = "https://heatpump-api.energytools.com/"

def analyze_options(ui_inputs):
  """Performs the full analysis of all heat pump options and As Installed case.
  'input_dict': The dictionary of all the model inputs.
  """
  anvil.server.call('pprint', ui_inputs)

def make_api_analyze_inputs(ui_inputs):
  # shortcut variable
  inp = ui_inputs

  # Energy Prices sub-dictionary
  energy_prices = {
    
  }

  # Tuple containing Primary and Secondary conventional heating systems
  conventional_systems = (
    {
      
    },
    {
      
    }
  )
  
  building = {
'''
  'city_id': inp['model_city'],
  'energy_prices': energy_prices,
  'conventional_heat': conventional_systems,
  'heat_pump': None,
  'garage_stall_count': inp['garage_count'],
  'bldg_floor_area': inp['floor_area'],
  'occupant_count': inp['occupant_count'],
  'indoor_heat_setpoint': 70.0,
  'ua_per_ft2': 0.19,    # will be changed in model fitting
  'dhw_fuel_id':        # ID of domestic hot water fuel
  'dhw_ef': float = 0.62                     # Energy Factor of DHW System
  'clothes_drying_fuel_id': Fuel_id | None = None   # ID of clothes drying fuel
  'cooking_fuel_id': Fuel_id | None = None   # ID of cooking fuel
  'misc_elec_kwh_per_day': 13.0,      # will be changed in model fitting
  'misc_elec_seasonality': 0.15,      # will be changed in model fitting
  'ev_charging_miles_per_day': float = 0.0           # average miles / day of home EV charging
  'ev_miles_per_kwh': 3.0,            # will be changed in model fitting
  'ev_seasonality': 0.0,              # will be changed in model fitting
  'solar_kw': float = 0.0             # kW of home PV solar
  'solar_kwh_per_kw': 650.0,             # will be changed in model fitting
'''
  }

  return bldg

def calculate_results(inputs):

  resp = anvil.http.request(
    CALCULATOR_API_BASE_URL + 'energy/energy-model',
    method="POST",
    data=inputs,
    json=True
  )
  anvil.server.call('pprint', resp)