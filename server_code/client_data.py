"""Functions for working with ClientData
"""
from typing import Any, Dict, List

import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from anvil.users import get_user
import anvil.secrets

@anvil.server.callable
def get_clients() -> List[Dict[str, Any]]:
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

@anvil.server.callable
def get_client(row_id: str) -> Dict[str, Any]:
  """Returns a dictionary of field values for the Client identified by 'row_id'.
  Returns None if there is no matching client.
  """
  if get_user():
    client = app_tables.clientdata.get_by_id(row_id)
    if client:
      fields = {'row_id': row_id}
      fields.update(dict(client))
      return fields
    
    else:
      return None
