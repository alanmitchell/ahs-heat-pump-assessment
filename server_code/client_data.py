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
def add_update_client(row_id: str, fields: Dict[str, Any]) -> bool:
  """Adds a New Client or Updates the fields of an Existing Client. 'row_id' identifies the Client row
  to update. If 'row_id' is None, a new client is added. 'fields' is a dictionary of the field values that 
  need to be updated for the Client.  If the Add or Update is successful, the Row ID of the Client is returned.
  If no success, False is returned.
  Only logged in Users can call this function.
  """
  def clean_fields(field_dict):
    """This function cleans up the field value dictionary so that it can be used to update or
    add a row in the ClientData table.
    """
    if 'assessor_id' in field_dict:
      assessor_id = field_dict.pop('assessor_id')
      # get the assessor row associated with this assessor ID
      assessor = app_tables.users.get_by_id(assessor_id)
      field_dict['assessor'] = assessor
      
  if get_user():
    # clean up the field value dictionary
    try:
      clean_fields(fields)
    except:
      # the assessor probably does not exist
      return False

    if row_id:
      # retrieve the client row
      client = app_tables.clientdata.get_by_id(row_id)
      if client:
        client.update(**fields)
        return row_id
      else:
        return False
    else:
      # Add a new Client
      new_client = app_tables.clientdata.add_row(**fields)
      return new_client.get_id()
  else:
    # No logged in User
    return False
