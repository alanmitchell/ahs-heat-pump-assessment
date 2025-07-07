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
  return [
    {'id': u.get_id(), 'email': u['email'], 'is_staff': u['is_staff']}
    for u in app_tables.users.search()
  ]
