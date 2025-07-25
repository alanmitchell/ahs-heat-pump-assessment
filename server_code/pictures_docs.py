import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_pics_for_current_user():
  #cur_user = anvil.users.get_user()
  cur_user = app_tables.users.get(email='tabb99@gmail.com')
  if cur_user:
    result = app_tables.pictures.search(client=cur_user)
    result_dicts = []
    for row in result:
      pic_info = dict(row)
      pic_info['row_id'] =  row.get_id()
      result_dicts.append(pic_info)
    return result_dicts
  else:
    return []



def store_pics_for_current_user():
  pass