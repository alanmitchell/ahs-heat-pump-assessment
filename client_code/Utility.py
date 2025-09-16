"""Utility functions.
"""
from anvil.users import get_user
import anvil.server


def chg_none(val, none_replacement=""):
  """Returns 'val' unless it is None, whereupon it return 'none_replacement'.
  """
  return val if val is not None else none_replacement

def chg_none_blank(val: str, replacement=""):
  """Returns 'val' unless it is None or Blank, whereupon it returns 'replacement'.
  Assumes 'val' is a string.
  """
  if val is None or len(val)==0:
    return replacement
  else:
    return val

def active_client_name():
  """Returns the name of the currently active client, if there is one. 
  Returns empty string otherwise.
  """
  cur_user = get_user()
  if cur_user:
    last_client_id = cur_user['last_client_id']
    if last_client_id:
      return chg_none(anvil.server.call('get_client', last_client_id)['full_name'], '')
