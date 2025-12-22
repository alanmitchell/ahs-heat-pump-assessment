from typing import Any
from datetime import timedelta, datetime

import numpy as np

import anvil.server
from anvil.users import get_user

from .client_data import get_client
from .google_util import get_sheet_values
from .util import convert

# maps day of year to cumulative oil use through that day.
# Based on modeling a 2200 square foot Juneau home assuming Space and DHW end uses
# are served by Oil.  See gdrive/alaska-heat-smart/hp-calculator/actual-use/oil-use.xlsx
OIL_DAY_NUM = np.array([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365])
OIL_CUM_USE = np.array([0.0, 0.146, 0.264, 0.385, 0.461, 0.511, 0.549, 0.583, 0.623, 0.674, 0.754, 0.867, 1.000])

def fills_to_use(range_string: str | None, method: str) -> float:
  """Converts a string generated from the custom Google Sheets function RANGE_TO_LIST into an
  annual usage value. The 'range_str' is the RANGE_TO_LIST of a two-column range containing
  fill dates and fill amounts.  RANGE_TO_LIST converts dates into serial numbers using the Excel
  date representation (0 = 12/30/1899).
  'method' indicates the pattern of usage assumed. A value of 'linear' means constant, non-seasonal
  usage. A value of 'oil' means seasonal usage following the pattern indicated by OIL_CUM_USE.
  The return value is a float value equal to the average annual usage implied by the data. 
  If there are problems with the data, an error is raised.
  """
  if range_string is None:
    # no fuel if the range is empty
    return 0.0

  def convert_val(x):
    # If x looks like an Excel datetime serial number, return the associated Python datetime
    # value. Otherwise return the float value of x. Raise an error if x is non-numeric.
    try:
      float_x = float(x)
    except ValueError:
      raise ValueError('Bad Formatted Fill Data.')

    if float_x > 40000:
      # it's a date
      return datetime(1899, 12, 30) + timedelta(days=float_x)
    else:
      # should be a number
      return float_x

  state = 'find start date'
  start_date = None
  last_date = None
  total_use = 0.0
  for val in range_string.split('|'):
    val = convert_val(val)
    match state:
      case 'find start date':
        if type(val) is datetime:
          start_date = val
          state = 'find second date'   # cuz need to skip any first fill value
      case 'find second date':
        if type(val) is datetime:
          last_date = val
          state = 'summing fills'
      case 'summing fills':
        if type(val) is datetime:
          last_date = val
        else:
          total_use += val

  if state != 'summing fills' or last_date is None:
    raise ValueError('Bad formatted fill data.')
  else:
    # calculate annual average use
    # make a function that converts the day of the year (1 - 366) into a cumulative fraction
    # of fuel use.
    match method:
      case 'oil':
        day_to_frac_use = lambda doy: np.interp(doy, OIL_DAY_NUM, OIL_CUM_USE)
      case 'linear':
        day_to_frac_use = lambda doy: doy / 365.0
      case _:
        raise ValueError('Unsupported value for "method".')
    start_yr = start_date.year + day_to_frac_use(start_date.timetuple().tm_yday)
    end_yr = last_date.year + day_to_frac_use(last_date.timetuple().tm_yday)
    
    return float(total_use / (end_yr - start_yr))      # converts np.float to regular float

@anvil.server.callable
def get_actual_use(client_id):
  """Returns a dictionary of actual fuel and electricity use for a Client with the
  ID of 'client_id'.
  """
  if get_user():
    # only excecute for logged-in Users
    client = get_client(client_id, ('historical_use_file_id', ))
    if client:
      variables = {}
      values = get_sheet_values(client['historical_use_file_id'], 'Output')
      for row in values:
        # row is a 1 or 2-element list. The first element is the variable name,
        # and the second, if present, is the value. If not present there is not value
        # for that variable.
        if len(row) == 2:
          variables[row[0]] = row[1]
        else:
          variables[row[0]] = None

      # process the variables
      err_msgs = []
      for var, val in variables.items():
        try:
          match var:
            case 'spruce_cords' | 'birch_cords' | 'pellet_pounds':
              try:
                variables[var] = float(convert(val, (None,), 0.0))
              except (TypeError, ValueError):
                raise ValueError('Cannot convert cell contents to a number.')
  
            case 'oil_fills':
              variables[var] = fills_to_use(val, 'oil')

            case 'propane_fills':
              variables[var] = fills_to_use(val, 'linear')

            case 'electricity_monthly':
              try:
                mo_vals = [float(x) for x in val.split('|')]
              except Exception as e:
                raise ValueError('One or more monthly values is missing or not a number.')
              variables[var] = mo_vals

            case 'ng_use':
              try:
                mo_vals = [float(x) for x in val.split('|')]
              except Exception as e:
                raise ValueError('One or more monthly values is missing or not a number.')
              variables[var] = sum(mo_vals)

        except Exception as e:
          err_msgs.append(f'Error processing {var}: {e}')

      if len(err_msgs):
        final_msg = ', '.join(err_msgs)
        raise ValueError(final_msg)
      else:
        print(variables)
  # if we got to here, no User or client
  return {}