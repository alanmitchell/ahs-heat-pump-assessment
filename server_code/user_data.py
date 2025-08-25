import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_users_public_fields():
  """Returns publicly-viewable User fields."""
  return [
    {'id': u.get_id(), 'email': u['email'], 'full_name': u['full_name']}
    for u in app_tables.users.search()
  ]

@anvil.server.callable
def user_processing_at_login(user_id):
  """Does any server-side processing that is needed after a user logs in."""
  cur_user = anvil.users.get_user()

@anvil.server.callable
def update_user_info(field_dict):
  """Updates User fields for currently logged in User.
  'field_dict' has the the field names and values that
  are to be changed."""
  cur_user = anvil.users.get_user()
  if cur_user:
    for field_name, val in field_dict.items():
      cur_user[field_name] = val
