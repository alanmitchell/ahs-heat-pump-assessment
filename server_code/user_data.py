import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def update_is_staff(user_id, new_value):
  user = app_tables.users.get_by_id(user_id)
  if user:
    user['is_staff'] = new_value

@anvil.server.callable
def get_users_public_fields():
  """Returns publicly-viewable User fields."""
  return [
    {'id': u.get_id(), 'email': u['email'], 'is_staff': u['is_staff']}
    for u in app_tables.users.search()
  ]

@anvil.server.callable
def user_processing_at_login(user_id):
  """Does any server-side processing that is needed after a user logs in."""
  user = app_tables.users.get_by_id(user_id)
  if user:
    # check to see if user has an Alaska Heat Smart email, and if so, make them a 
    # staff user.
    if user['email'].lower().endswith('akheatsmart.org'):
      # only do this one time (field is None initially)
      if user['is_staff'] is None:
        user['is_staff'] = True
