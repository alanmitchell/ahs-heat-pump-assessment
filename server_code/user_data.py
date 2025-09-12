from typing import Any, Dict, List, Optional

import anvil.secrets
import anvil.users
from anvil.users import get_user
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_users_public_fields() -> List[Dict[str, Any]]:
  """Returns publicly-viewable User fields."""
  if get_user():
    return [
      {'id': u.get_id(), 'email': u['email'], 'full_name': u['full_name']}
      for u in app_tables.users.search()
    ]

@anvil.server.callable
def user_processing_at_login():
  """Does any server-side processing that is needed after a user logs in."""
  cur_user = get_user()

@anvil.server.callable
def update_user_info(field_dict):
  """Updates User fields for currently logged in User.
  'field_dict' has the the field names and values that
  are to be changed. Returns True if update occurred."""
  cur_user = get_user()
  if cur_user:
    for field_name, val in field_dict.items():
      cur_user[field_name] = val
      return True
  else:
    return False

ALLOWED_DOMAINS = {"akheatsmart.org", "analysisnorth.com"}
@anvil.server.callable
def restricted_signup(email: str, password: str):
  # Basic sanity check
  if not email or "@" not in email:
    raise Exception("Please provide a valid email address.")

  domain = email.split("@")[-1].lower()
  if domain not in ALLOWED_DOMAINS:
    allowed = ", ".join(sorted(ALLOWED_DOMAINS))
    raise Exception(f"Sign-up is restricted to: {allowed}")

    # Create the user; Users service will send a confirmation email
    # if you have 'Require email confirmation' enabled.
  anvil.users.signup_with_email(email, password)
  return True

