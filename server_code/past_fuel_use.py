import anvil.server
from anvil.users import get_user

from .client_data import get_client
from .google_util import get_sheet_values

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
      print(variables)
      for var, val in variables.items():
        match var:
          case 'spruce_cords' | 'birch_cords' | 'pellet_pounds':
            # convert non-numeric to 0.0
            try:
              variables[var] = float(val)
            except (TypeError, ValueError):
              variables[var] = 0.0
      print(variables)
  # if we got to here, no User or client
  return {}