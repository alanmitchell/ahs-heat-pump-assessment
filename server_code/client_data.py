import anvil.secrets
"""Functions for working with ClientData
"""
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil.users import get_user

@anvil.server.callable
def get_clients():
  """Returns a list of clients, each item being a dictionary of fields for that client.
  """
  if get_user():
    # only allows for logged in users.  Include the row ID as well as all the fields.
    rows = []
    for c in app_tables.clientdata.search():
      row = {'row_id': c.get_id()}
      row.update(dict(c))
      rows.append(row)
    return rows
