import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_all_media_for_user(user_id):
  """Returns all the pictures/documents associated with the client having
  a user ID of 'user_id'.
  """
  user = app_tables.users.get_by_id(user_id)
  if user:
    result = app_tables.media.search(client=user)
    result_dicts = []
    for row in result:
      media_info = dict(row)
      media_info['row_id'] =  row.get_id()
      result_dicts.append(media_info)
    return result_dicts
  else:
    return []

@anvil.server.http_endpoint("/get-media/:row_id")
def get_media(row_id):
  """Return the media object contained in the Media table row identified
  by 'row_id'.
  """
  media_row = app_tables.media.get_by_id(row_id)
  if media_row:
    return media_row['media_object']
  else:
    return None

def store_media(user_id, media_info):
  """Stores a changed or new piece of media for a client identified by 'user_id'. 'media_info'
  is a dictionary with 'media_object', 'category', 'caption', and 'row_id' keys. 'row_id' is the 
  ID for an existing piece of media. If 'row_id' is not found, that indicates a new piece of media is
  being stored, and a new record in the Media table is created.
  The function returns the row ID of the Media record, which is particularly useful it a new record
  was added.
  """
  media_row_id = media_info['row_id']
  row = app_tables.media.get_by_id(media_row_id)
  if row:
    for key, value in media_info:
      if key != 'row_id':
        row[key] = value
  else:
    # need to add a new record
    user = app_tables.users.get_by_id(user_id)
    if user:
      field_dict = media_info.copy()
      del field_dict['row_id']
      field_dict['client'] = user
      new_row = app_tables.media.add_row(**field_dict)
      media_row_id = new_row.get_id()

  return media_row_id