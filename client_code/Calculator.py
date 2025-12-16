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
  
  api_inp = {
'''
  'city_id': inp['model_city]

  energy_prices: EnergyPrices    # Energy price information for the building

  # Description of non-heat-pump heating systems: primary and secondary (optional)
  conventional_heat: Tuple[ConventionalHeatingSystem, ConventionalHeatingSystem | None]

  heat_pump: HeatPump | None = (
    None  # Description of Heat Pump. If None, then no heat pump.
  )
  
  garage_stall_count: int  # 0: No garage, 1: 1-car garage.  Max is 4.
  bldg_floor_area: (
    float  # Floor area in square feet of home living area, not counting garage.
  )
  occupant_count: float = 3.0    # Number of occupants for estimating non-space energy use
  indoor_heat_setpoint: float = 70.0  # Indoor heating setpoint, deg F
  ua_per_ft2: float    # UA per square foot for main home
  
  dhw_fuel_id: Fuel_id | None = None       # ID of domestic hot water fuel
  dhw_ef: float = 0.62                     # Energy Factor of DHW System
  clothes_drying_fuel_id: Fuel_id | None = None   # ID of clothes drying fuel
  cooking_fuel_id: Fuel_id | None = None   # ID of cooking fuel
  
  # annual average kWh/day for lights and miscellaneous appliances end uses. 
  # Does not include space htg, dhw, cooking, and clothes drying, EV charging, or solar.
  misc_elec_kwh_per_day: float = 13.0
  
  # +/- deviation in use/day from average for December and June. 
  # Expressed as a fraction of the average. If positive
  # December is higher than average and June is lower. If negative,
  # December is lower than average and June higher (perhaps snowbird usage pattern)
  misc_elec_seasonality: float = 0.15  
  
  # Infomration about Home EV charging electricity use.
  ev_charging_miles_per_day: float = 0.0           # average miles / day of home EV charging
  ev_miles_per_kwh: float = 3.0            # Average miles driven per kWh of charge
  ev_seasonality: float = 0.0              # Variation of Dec EV kWh/day compared to average, fraction
  
  solar_kw: float = 0.0                    # kW of home PV solar
  solar_kwh_per_kw: float = 700.0          # Annual kWh produced per solar kW installed
  
'''
  }

  return api_inp

def calculate_results(inputs):

  resp = anvil.http.request(
    CALCULATOR_API_BASE_URL + 'energy/energy-model',
    method="POST",
    data=inputs,
    json=True
  )
  anvil.server.call('pprint', resp)