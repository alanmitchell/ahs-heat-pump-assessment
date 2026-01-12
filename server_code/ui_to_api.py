"""Functions to convert values collected by the UI into dictionaries that can
be used with the Heat Pump Calculator API.
"""
import math
from copy import deepcopy

from anvil.tables import app_tables

from .check_inputs import check_option_inputs
from .util import convert, dval

# ----- Auxiliary electric use values (kWh / MMBTU output) for all possible heating system types
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

def make_base_bldg_inputs(ui_inputs):
  """Creates the dictionary of API inputs for the base, pre-heat-pump
  building using the UI inputs from 'ui_inputs'.
  """
  # shortcut variable
  inp = ui_inputs

  # Energy Prices sub-dictionary
  fuel_name_to_id = {
    'oil_price': 'oil1', 
    'propane_price': 'propane', 
    'ng_price': 'ng', 
    'birch_price': 'birch', 
    'spruce_price': 'spruce', 
    'pellet_price': 'pellets'
  }
  energy_prices = {
    'utility_id': inp['rate_sched'],
    'pce_limit': 750.0,
    'elec_rate_override': None,
    'pce_rate_override': None,
    'customer_charge_override': None,
    'co2_lbs_per_kwh_override': None,
    'fuel_price_overrides': {fuel_id: inp[fuel_name] for fuel_name, fuel_id in fuel_name_to_id.items() if inp.get(fuel_name) not in (None, '')},
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
    dhw_ef = conventional_systems[0]['heating_effic'] * 0.96     # Assume 4% tank losses
    hpwh_source = None
  else:
    dhw_fuel = inp['dhw_fuel']
    dhw_ef = inp['ef_dhw']
    hpwh_source = inp['hpwh_source'] if inp['dhw_sys_type'] == 'hpwh' else None

  existing_building = {
    'city_id': inp['model_city'],
    'energy_prices': energy_prices,
    'conventional_heat': conventional_systems,
    'heat_pump': None,
    'garage_stall_count': convert(inp.get('garage_count'), (None, ''), 0),
    'bldg_floor_area': inp['floor_area'],
    'occupant_count': convert(inp.get('occupant_count'), (None, ''), 0.0),
    'indoor_heat_setpoint': 70.0,
    'ua_per_ft2': 0.19,              # will be changed in model fitting
    'dhw_fuel_id': dhw_fuel,
    'dhw_ef': dhw_ef,
    'dhw_hpwh_source': hpwh_source,
    'clothes_drying_fuel_id': inp.get('drying_fuel'),
    'cooking_fuel_id': inp.get('cooking_fuel'),
    'misc_elec_kwh_per_day': 13.0,      # will be changed in model fitting
    'misc_elec_seasonality': 0.15,      # will be changed in model fitting
    'ev_charging_miles_per_day': convert(inp.get('ev_charging_miles_per_day'), (None, ''), 0.0),
    'ev_miles_per_kwh': 3.0,            # will be changed in model fitting
    'ev_seasonality': 0.0,              # will be changed in model fitting
    'solar_kw': convert(inp.get('solar_kw'), (None, ''), 0.0),
    'solar_kwh_per_kw': 650.0,             # will be changed in model fitting
  }

  return existing_building

def make_energy_model_fit_inputs(base_bldg, actual_fuel_use):
  """Makes the energy model fit inputs for the Heat Pump Calculator API.
  """
  fuel_use = {
    'ng': actual_fuel_use['ng_ccf'],
    'propane': actual_fuel_use['propane_gal'],
    'oil1': actual_fuel_use['oil_gal'],
    'birch': actual_fuel_use['birch_cords'],
    'spruce': actual_fuel_use['spruce_cords'],
    'pellets': actual_fuel_use['pellet_pounds'],
  }
  return {
    "building_description": base_bldg,
    "actual_fuel_by_type": fuel_use,
    "electric_use_by_month": actual_fuel_use['electricity_monthly'],
  }

def make_option_building(base_bldg, option):
  """Returns a building description dictionary created by modifying the "base_bldg"
  in accordance with the retrofits described in "option". If there are input errors,
  return a string describing the input problems.
  """
  # Check for inputs errors in the heat pump options
  option_errors = check_option_inputs(option)
  if option_errors:
    return ' '.join(option_errors)
    
  else:
    # modify the base building in accordance with the Option description
    bldg = deepcopy(base_bldg)
    heat_pump = {
      'source_type': option['hp_source'],
      'hspf_type': 'hspf2_reg5',
      'hspf': convert(option.get('hspf2'), ('',), None),
      'cop_32f': convert(option.get('cop32f'), ('',), None),
      'max_out_5f': option['max_capacity'] if option['hp_source']=='air' else None,
      'max_out_32f': option['max_capacity'] if option['hp_source']!='air' else None,
      'low_temp_cutoff': 5.0,
      'off_months': None,
      'frac_exposed_to_hp': option['load_exposed'] / 100.0,
      'frac_adjacent_to_hp': option['load_adjacent'] / 100.0,
      'doors_open_to_adjacent': True,
      'bedroom_temp_tolerance': 'med',
      'serves_garage': True if dval(option, 'garage_served_by_hp') else False,
    }
    bldg['heat_pump'] = heat_pump

    # Load not served by heat pump.  Only one additional heating systme is used.
    match option['unserved_source']:
      case 'primary':
        # correct heating system in the primary slot already.
        pass

      case 'secondary':
        # Prior to this, make sure secondary inputs are OK
        # copy secondary system into primary position
        bldg['conventional_heat'][0] = deepcopy(bldg['conventional_heat'][1])

      case 'other':
        heater = {
          'heat_fuel_id': option['heating_system_unserved']['fuel'],
          'heating_effic': option['heating_system_unserved']['efficiency'] / 100.0,
          'aux_elec_use': HEATING_SYS_AUX[option['heating_system_unserved']['system_type']],
        }
        bldg['conventional_heat'][0] = heater

    # Primary system serves all load after heat pump tries.
    bldg['conventional_heat'][0]['frac_load_served'] = 1.0
    bldg['conventional_heat'][1]['frac_load_served'] = 0.0

    # DHW system with Heat Pump
    match option['dhw_source']:
      case 'as-before':
        dhw_fuel = bldg['dhw_fuel_id']
        dhw_ef = bldg['dhw_ef']
        hpwh_source = bldg['dhw_hpwh_source']

      case 'from-space-hp':
        # Space heating heat pump is being used for DHW as well. Base the DHW efficiency
        # off of the COP of that heat pump.
        
        if option.get('hspf2'):
          # assume an HSPF2-region V of 10 corresponds to a seasonal COP of 2.6. This comes
          # from experience with measured field data in Alaska. Ratio from
          # that using a square-root function to dampen the change.
          space_cop = math.sqrt(option['hspf2'] / 10.0) * 2.6
        else:
          # COP @ 32F must have been provided.
          space_cop = option['cop32f']

        # High COP units probably are producing low temperature water (~ 100F) so need resistance
        # supplment to achieve DHW temperature water. So need to downgrade COP to get the
        # DHW efficiency. Also, tank losses for water heating reduce COP; use a 0.96 multiplier
        # for that.
        if space_cop > 1.6:
          # space_cop of 1.6 is DHW EF of 1.6, linear to space_cop of 2.6 -> 2.0 EF, not
          # adjusting for tank losses.
          dhw_ef = (space_cop - 1.6) * 0.4 + 1.6
        else:
          dhw_ef = space_cop
        dhw_ef *= 0.96         # tank losses
        dhw_fuel = 'elec'
        hpwh_source = 'outdoors'

      case 'new-tank' | 'new-tankless':
        dhw_fuel = option['dhw_after_fuel']
        dhw_ef = option['ef_new_dhw']
        hpwh_source = None

      case 'new-hpwh':
        dhw_fuel = 'elec'
        dhw_ef = option['ef_new_dhw']
        hpwh_source = option['hpwh_source']

    bldg['dhw_fuel_id'] = dhw_fuel
    bldg['dhw_ef'] = dhw_ef
    bldg['dhw_hpwh_source'] = hpwh_source
  
    return bldg

def make_econ_inputs():
  """Returns the dictionary of economic inputs used by the retrofit analysis in the Calculator API.
  """
  general_inflation = float(app_tables.settings.search(key="general-inflation")[0]["value"])
  disc_rate_real = float(app_tables.settings.search(key="discount-rate-real")[0]["value"])
  elec_esc_real = float(app_tables.settings.search(key="elec-rate-esc-real")[0]["value"])
  fuel_esc_real = float(app_tables.settings.search(key="fuel-price-esc-real")[0]["value"])
  
  return {
    'elec_rate_forecast': (1.0 + general_inflation) * (1.0 + elec_esc_real) - 1.0,
    'fuel_price_forecast': (1.0 + general_inflation) * (1.0 + fuel_esc_real) - 1.0,
    'discount_rate': (1.0 + general_inflation) * (1.0 + disc_rate_real) - 1.0,
    'inflation_rate': general_inflation
  }

def make_retrofit_cost(option):
  """Returns a dictionary of retrofit cost inputs for the Heat Pump Option 'option'.
  In the format necessary for the Calculator API.
  """
  capital_cost = \
    convert(option.get('cost_hp_install'), (None, ''), 0.0) + \
    convert(option.get('cost_electrical'), (None, ''), 0.0) + \
    convert(option.get('cost_permit'), (None, ''), 0.0) + \
    convert(option.get('cost_non_hp'), (None, ''), 0.0)
  rebate_amount = \
    convert(option.get('hp_incentives'), (None, ''), 0.0) + \
    convert(option.get('hp_tax_credit'), (None, ''), 0.0)
  
  return {
    'capital_cost': capital_cost,
    'rebate_amount': rebate_amount,
    'retrofit_life': int(app_tables.settings.search(key="retrofit-life")[0]["value"]),
    'op_cost_chg':  0.0,
    'loan_amount': 0.0,
    'loan_term': None,
    'loan_interest': None,
  }
