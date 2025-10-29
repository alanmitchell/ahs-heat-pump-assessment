"""Functions for working with ClientData
"""
from typing import Any, Dict, List, Optional

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
def get_client(row_id: str, field_subset: tuple[str]=None) -> Optional[Dict[str, Any]]:
  """Returns a dictionary of field values for the Client identified by 'row_id'.
  Returns None if there is no matching client. 'field_subset' can contain a tuple
  of desired fields, and only those will be returned.
  """
  if get_user():
    client = app_tables.clientdata.get_by_id(row_id)
    if client:
      fields = {'row_id': row_id}
      if field_subset:
        for field_name in field_subset:
          fields[field_name] = client[field_name]
      else:
        fields.update(dict(client))
      return fields
    
    else:
      return None

@anvil.server.callable
def update_client(row_id: str, fields: Dict[str, Any]) -> bool:
  """Updates the fields of a Client data row. 'row_id' identifies the Client row
  to update. 'fields' is a dictionary of the field values that need to be updated.
  """
  if get_user():
    # retrieve the client row
    client = app_tables.clientdata.get_by_id(row_id)
    if client:
      for field_name, val in fields.items():
        if field_name == 'assessor_id':
          # special case: the actual field, 'assessor' is a DataTable row
          assessor = app_tables.users.get_by_id(val)
          if assessor:
            client['assessor'] = assessor
        else:
          client[field_name] = val
      return True
    else:
      return False
  else:
    return False
