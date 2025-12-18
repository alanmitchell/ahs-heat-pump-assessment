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
  fuel_price_names = ('oil_price', 'propane_price', 'ng_price', 'birch_price', 'spruce_price', 'pellet_price')
  energy_prices = {
    'utility_id': inp['rate_sched'],
    'pce_limit': 750.0,
    'elec_rate_override': None,
    'pce_rate_override': None,
    'customer_charge_override': None,
    'co2_lbs_per_kwh_override': None,
    'fuel_price_overrides': {fuel: inp[fuel] for fuel in fuel_price_names if inp[fuel] is not None},
    'sales_tax_override': None
  }

  # Tuple containing Primary and Secondary conventional heating systems
  conventional_systems = (
    {
      
    },
    {
      
    }
  )

  # determine DHW API inputs
  if inp['dhw_sys_type'] == 'from-space-htr':
    dhw_fuel = conventional_systems[0]['heat_fuel_id']
    dhw_ef = conventional_systems[0]['heating_effic'] - 0.05     # 5% less than Primary Space Heating Efficiency
  else:
    dhw_fuel = inp['dhw_fuel']
    dhw_ef = inp['ef_dhw']
  
  existing_building = {
  'city_id': inp['model_city'],
  'energy_prices': energy_prices,
  'conventional_heat': conventional_systems,
  'heat_pump': None,
  'garage_stall_count': inp['garage_count'],
  'bldg_floor_area': inp['floor_area'],
  'occupant_count': inp['occupant_count'],
  'indoor_heat_setpoint': 70.0,
  'ua_per_ft2': 0.19,              # will be changed in model fitting
  'dhw_fuel_id': dhw_fuel,
  'dhw_ef': dhw_ef,      
  'clothes_drying_fuel_id': inp['drying_fuel'],
  'cooking_fuel_id': inp['cooking_fuel'],
  'misc_elec_kwh_per_day': 13.0,      # will be changed in model fitting
  'misc_elec_seasonality': 0.15,      # will be changed in model fitting
  'ev_charging_miles_per_day': inp['ev_charging_miles_per_day'],
  'ev_miles_per_kwh': 3.0,            # will be changed in model fitting
  'ev_seasonality': 0.0,              # will be changed in model fitting
  'solar_kw': inp['solar_kw'],
  'solar_kwh_per_kw': 650.0,             # will be changed in model fitting
  }

  return existing_building

def calculate_results(inputs):

  resp = anvil.http.request(
    CALCULATOR_API_BASE_URL + 'energy/energy-model',
    method="POST",
    data=inputs,
    json=True
  )
  anvil.server.call('pprint', resp)