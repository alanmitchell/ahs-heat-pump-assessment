"""Functioions to check the validity of User inputs are here.
"""
from .util import dval

def check_vars(var_check_list, input_dict):
  """Checks the validity of a list of variables (var_check_list) appearing in a dictionary
  of inputs (input_dict). Any errors found are put in a list of error messages are returned.
  See the 'check_main_model_inputs' for an example of the format of 'var_check_list'.
  """
  msg_list = []

  for var_info in var_check_list:

    var, var_label, is_required = var_info[:3]
    val = dval(input_dict, var)

    # if required, test it
    if is_required and val in (None, ''):
      msg_list.append(f'{var_label} is required.')

    # loop through any other test present, if the value is present
    if val not in (None, ''):
      for test in var_info[3:]:
        if not eval(f'{val} {test}'):
          msg_list.append(f'{var_label} must be {test}.')

  return msg_list

def check_main_model_inputs(inp):
  """Checks the main model inputs for errors. Returns empty list if error-free. Returns
  a list of error messages if there are input problems
  """

  # Info and constraints on inputs. Format is:
  # (variable, variable label, required?, 0 or more conditions the variable value must be if the variable is present)
  vars = (
    ('model_city', 'Modeling City', True),
    ('rate_sched', 'Electric Rate Schedule', True),
    ('year_built', 'Year Built', True, '>= 1880'), 
    ('floor_area', 'Floor Area', True, '> 0', '< 15000'),
    ('garage_count', 'Heated Garage Size', True),
    ('occupant_count', 'Occupant Count', True, '> 0', '<= 15'),
    ('electrical_service', 'Electrical Service size', True, '> 0', '<= 400'),
    ('heating_system_primary.fuel', 'Primary Heating System Fuel type', True),
    ('heating_system_primary.system_type', 'Primary Heating System System Type', True),
    ('ev_charging_miles_per_day', 'Miles per Day of EV Charging', False, '> 0', '< 300'),
    ('solar_kw', 'kW of Solar Panels', False, '> 0', '<= 30')
  )

  msgs = check_vars(vars, inp)

  # Custom Checks below

  # Check to make sure there are fuel prices for every fuel used inin the model.
  # First find all the fuels used by the existing building and heat pump options. (Not concerned
  # about electricity).
  fuels = set()
  fuels.add(dval(inp, 'heating_system_primary.fuel'))
  fuels.add(dval(inp, 'heating_system_secondary.fuel'))
  if dval(inp, 'dhw_sys_type') in ('tank', 'tankless'):
    fuels.add(dval(inp, 'dhw_fuel'))
  fuels.add(dval(inp, 'cooking_fuel'))
  fuels.add(dval(inp, 'drying_fuel'))
  for option in inp['heat_pump_options']:
    if dval(option, 'unserved_source') == 'other':
      fuels.add(dval(option, 'heating_system_unserved.fuel'))
    if dval(option, 'dhw_source') in ('new-tank', 'new-tankless'):
      fuels.add(dval(option, 'dhw_after_fuel'))
  # get rid of the None if present
  if None in fuels:
    fuels.discard(None)
  print(fuels)

  # Start a list of variable checks
  vars = []

  # Primary Htg system efficiency
  sys_type = dval(inp, 'heating_system_primary.system_type')
  if sys_type in ('ashp', 'wshp', 'gshp'):
    vars += [('heating_system_primary.efficiency', 'Primary Heating System Efficiency', True, '> 100', '<= 450')]
  else:
    vars += [('heating_system_primary.efficiency', 'Primary Heating System Efficiency', True, '> 10', '<= 100')]

  # Details  on Secondary Heating System if present
  fuel_type = dval(inp, 'heating_system_secondary.fuel')
  if fuel_type not in (None, ''):
    vars += [('heating_system_secondary.system_type', 'Secondary Heating System System Type', True)]
    sys_type = dval(inp, 'heating_system_secondary.system_type')
    if sys_type in ('ashp', 'wshp', 'gshp'):
      vars += [('heating_system_secondary.efficiency', 'Secondary Heating System Efficiency', True, '> 100', '<= 450')]
    else:
      vars += [('heating_system_secondary.efficiency', 'Secondary Heating System Efficiency', True, '> 10', '<= 100')]

  # DHW related
  dhw_sys_type = dval(inp, 'dhw_sys_type')
  match dhw_sys_type:
    case None | "from-space-htr":
      # no further checks required
      pass
    case 'tank' | 'tankless':
      vars += [
        ('dhw_fuel', 'Hot Water Heating Fuel Type', True),
        ('ef_dhw', 'EF (Energy Factor) of Hot Water Heater', True, '> 0', '< 1.0')
      ]
    case 'hpwh':
      vars += [
        ('ef_dhw', 'EF (Energy Factor) of Hot Water Heater', True, '> 1.0', '< 5.0'),
        ('hpwh_source', 'Source of Heat for the Heat Pump Water Heater', True)
      ]
  
  msgs += check_vars(vars, inp)

  return msgs
  
def check_option_inputs(option):
  """Checks the heat pump option "option" for errors. Return empty list if error-free. Returns
  a list of error messages if there are input problems.
  """
  vars = (
    ('title', 'Title', True),
    ('hp_source', 'Heat Source', True),
    ('hp_distribution', 'Heat Distribution type', True),
    ('hspf2', 'HSPF2', False, '> 4', '<= 13'),
    ('cop32f', 'COP @ 32F', False, '> 1.0', '<= 4.5'),
    ('max_capacity', 'Maximum Heat Pump Capacity', True, '> 0', '<= 200000'),
    ('load_exposed', 'Percent of Main Home Load Exposed to Heat Pump', True, '> 0', '<= 100'), 
    ('load_adjacent', 'Percent of Main Home Load Adjacent to Heat Pump', True, '>= 0', '< 100'),
    ('unserved_source', 'Source of Load Not Served by Heat Pump', True),
    ('dhw_source', 'Domestic Hot Water Source', True),
    ('cost_hp_install', 'Heat Pump Installation Cost', True, '> 0', '< 100000'),
  )
  msgs = check_vars(vars, option)

  # do other, more custom, checks
  hspf2 = dval(option, 'hspf2')
  cop32f = dval(option, 'cop32f')
  hp_source = dval(option, 'hp_source')
  if hp_source == 'air':
    if hspf2 in (None, '') and cop32f in (None, ''):
      msgs.append('You must enter either an HSPF2 or a COP.')
  else:
    # ground and water must have a COP value
    if cop32f in (None, ''):
      msgs.append(('You must enter a COP @ 32 F for the Heat Pump.'))

  unserved_source = dval(option, 'unserved_source')
  if unserved_source == 'other':
    vars = (
      ('heating_system_unserved.fuel', 'Fuel Type of the Heating System for Non-heat pump Load', True),
      ('heating_system_unserved.system_type', 'System Type of the Heating System for Non-heat pump Load', True),
      ('heating_system_unserved.efficiency', 'Efficiency of the Heating System for Non-heat pump Load', True, '> 10', '<= 450'),
    )
    msgs += check_vars(vars, option)

  dhw_source = dval(option, 'dhw_source')
  match dhw_source:
    case "new-tank" | "new-tankless":
      vars = (
        ('dhw_after_fuel', 'Fuel used in New Water Heater', True),
        ('ef_new_dhw', 'EF (Energy Factor) of the New Water Heater', True, '> 0.2', '< 1.0')
      )
      msgs += check_vars(vars, option)
    case "new-hpwh":
      vars = (
        ('ef_new_dhw', 'EF (Energy Factor) of the New Heat Pump Water Heater', True, '> 1.0', '< 5.0'),
        ('hpwh_source', 'Source of Heat for New Heat Pump Water Heater', True)
      )
      msgs += check_vars(vars, option)
      
  return msgs
