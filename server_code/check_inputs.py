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
  )

  msgs = check_vars(vars, inp)

  return msgs
  
def check_option_inputs(option):
  """Checks the heat pump option "option" for errors. Return empty list if error-free. Returns
  a list of error messages if there are input problems.
  """
  vars = (
    ('title', 'Title', True),
    ('hp_source', 'Heat Source', True),
    ('hp_distribution', 'Heat Distribution type', True),
    ('hspf2', 'HSPF2', False, '> 0', '<= 13'),
    ('cop32f', 'COP @ 32F', False, '> 0', '<= 4.5'),
    ('max_capacity', 'Maximum Heat Pump Capacity', True, '> 0', '<= 200000'),
    ('load_exposed', 'Percent of Main Home Load Exposed to Heat Pump', True, '> 0', '<= 100'), 
    ('load_adjacent', 'Percent of Main Home Load Adjacent to Heat Pump', True, '>= 0', '< 100'),
    ('unserved_source', 'Source of Load Not Served by Heat Pump', True),
    ('dhw_source', 'Domestic How Water Source', True),
    ('cost_hp_install', 'Heat Pump Installation Cost', True, '> 0', '< 100000'),
  )
  msgs = check_vars(vars, option)

  # do other, more custom, checks
  hspf2 = dval(option, 'hspf2')
  cop32f = dval(option, 'cop32f')
  if hspf2 in (None, '') and cop32f in (None, ''):
    msgs.append('You must enter either an HSPF2 or a COP.')

  unserved_source = dval(option, 'unserved_source')
  if unserved_source == 'other':
    vars2 = (
      ('heating_system_unserved.fuel', 'Fuel Type of the Heating System for Non-heat pump Load', True),
      ('heating_system_unserved.system_type', 'System Type of the Heating System for Non-heat pump Load', True),
      ('heating_system_unserved.efficiency', 'Efficiency of the Heating System for Non-heat pump Load', True, '> 0', '<= 450'),
    )
    msgs += check_vars(vars2, option)

  return msgs
