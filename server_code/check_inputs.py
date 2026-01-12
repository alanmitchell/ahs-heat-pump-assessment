"""Functioions to check the validity of User inputs are here.
"""
from .util import dval

def check_main_model_inputs(inp):
  """Checks the main model inputs for errors. Returns empty list if error-free. Returns
  a list of error messages if there are input problems
  """
  msgs = []

  vars = ('')

def check_option_inputs(option):
  """Checks the heat pump option "option" for errors. Return empty list if error-free. Returns
  a list of error messages if there are input problems.
  """
  msgs = []

  vars = ('title', 'hp_source', 'hp_distribution', 'hspf2', 'max_capacity',
          'load_exposed', 'load_adjacent', 'unserved_source', 'dhw_source', 'cost_hp_install')
  for var in vars:
    val = dval(option, var)

    def required(var_name):
      """Adds a message to 'msgs' if val is None. 'var_name' gives the name of the
      variable.
      """
      if val in (None, ''):
        msgs.append(f'{var_name} is required.')

    match var:

      case 'title':
        required('Title')

      case 'hp_source':
        required('Heat Source')

      case 'hp_distribution':
        required('Heat Distribution type')

      case 'hspf2':
        cop32f = dval(option, 'cop32f')
        if val in (None, '') and cop32f in (None, ''):
          msgs.append('You must enter either an HSPF2 or a COP.')
        if val not in (None, '') and (val <= 0.0 or val > 13.0):
          msgs.append('The HSPF2 must be greater than 0 and less than 13.0.')
        if cop32f not in (None, '') and (cop32f <= 0.0 or cop32f > 4.5):
          msgs.append('The COP @ 32F must be greater than 0 and less than 4.5.')

      case 'max_capacity':
        required('Maximum Capacity at 5 F')

      case 'load_exposed':
        required('Percent of Main Home Load exposed to Heat Pump')
        if val not in (None, '') and val <= 0:
          msgs.append('Percent of Main Home Load exposed to Heat Pump must be greater than 0.')

      case 'load_adjacent':
        required('Percent of Main Home Load adjacent to Heat Pump')

      case 'unserved_source':
        required('Source of load not served by Heat Pump')
        if val == 'other':
          val = dval(option, 'heating_system_unserved.fuel')
          required('Fuel type of the Heating System for non-heat pump load')
          val = dval(option, 'heating_system_unserved.system_type')
          required('System type of the Heating System for non-heat pump load')
          val = dval(option, 'heating_system_unserved.efficiency')
          required('Efficiency of the Heating System for non-heat pump load')
          if val not in (None, '') and val <= 0:
            msgs.append('Efficiency of the Heating System for non-heat pump load must be more than 0.')

      case 'dhw_source':
        required('Domestic How Water source')

      case 'cost_hp_install':
        required('Heat Pump Installation Cost')
        if val not in (None, '') and val <= 0:
          msgs.append('Heat Pump Installation Cost must be greater than 0.')

  return msgs
