"""Module for managing the interface to the backend Calculator API. Prepares inputs
from the UI to be used in the Heat Pump Calculator API.
"""
import anvil.server
import anvil.http

from .Utility import convert

# Base URL to access heat pump calculator API endpoints.
CALCULATOR_API_BASE_URL = "https://heatpump-api.energytools.com/"

# Auxiliary electric use values (kWh / MMBTU output) for all possible heating system types
HEATING_SYS_AUX = {
  None: 0.0,          # Secondary system may be None
  'ashp': 0.0,        # included in COP
  'stove': 0.0,       # e.g. wood stove, no electricity
  
  # 150 W for 25,000 BTU/hr output according to  See https://chatgpt.com/share/69443d58-3934-800c-90fb-7c12af04d8af
  # But, larger pellet stoves were addressed in this Chat: https://chatgpt.com/share/6944426a-2f18-800c-9728-eb9d72193f44
  # That chat said 50 - 150 W for 34 - 50,000 BTU/hr pellet stove, a much lower value.
  # I'll use 125 W for 40,000 BTU/hr which is 3.1 and adjust up to 3.7 for part-load operation.
  'pellet-stove': 3.7,   
  
  'wshp': 0.0,        # included in COP
  
  # Toyo L-530/560, 40 W electric for 22,000 BTU/hr output is 1.8 kWh/MMBTU but increase for
  # part-load.  See: https://chatgpt.com/share/69443f0c-5f10-800c-a1d5-cf241027a500
  'hi-effic-space': 2.3,

  # From https://chatgpt.com/share/6944426a-2f18-800c-9728-eb9d72193f44, gas/oil furnace is
  # 2 - 4% electric as fraction of energy output. 3% is 8.8 kWh/MMBTU. Generally cycles so no 
  # major part-load adjustment.
  'furnace': 8.8, 

  'no-elec-space': 0.0,        # fuel space heater not needing electricity
  'gshp': 0.0,         # included in COP
  'elec-space': 0.0,   # already in the main fuel use of heater

  # From https://chatgpt.com/share/6944426a-2f18-800c-9728-eb9d72193f44, hydronic boiler is
  # 0.5 - 2.0%.  Does not look like they are accounting for burner gun use.  I'll use 1.5%,
  # which is 4.4 kWh/MMBTU
  'boiler': 4.4,
}

def analyze_options(ui_inputs):
  """Performs the full analysis of all heat pump options and As Installed case.
  'input_dict': The dictionary of all the model inputs.
  """
  #anvil.server.call('pprint', ui_inputs)
  api_inputs = make_api_analyze_inputs(ui_inputs)
  anvil.server.call('pprint', api_inputs)

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

  # --- Conventional Heating Systems
  aux_use = HEATING_SYS_AUX[inp['heating_system_primary']['system_type']]
  primary_info = {
    'heat_fuel_id': inp['heating_system_primary']['fuel'],
    'heating_effic': inp['heating_system_primary']['efficiency'] / 100.0,
    'aux_elec_use': aux_use,
    'frac_load_served': 1.0      # will be adjusted during model fitting
  }
  fuel = inp['heating_system_secondary'].get('fuel')
  sys_type = inp['heating_system_secondary'].get('system_type')
  aux_use = HEATING_SYS_AUX[sys_type]
  effic = inp['heating_system_secondary'].get('efficiency')
  # if missing or 0.0 convert to 80% to protect against divide by zero in Calc API
  effic = convert(effic, (None, '', 0.0), 80.0) / 100.0
  secondary_info = {
    'heat_fuel_id': fuel,
    # prior error check will ensure value if fuel is not None
    'heating_effic': effic,
    'aux_elec_use': aux_use,
    'frac_load_served': 0.0      # will be adjusted during model fitting
  }
  # Tuple containing Primary and Secondary conventional heating systems
  conventional_systems = (primary_info, secondary_info)

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