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

def text_to_float(tb_control):
  """Returns the value of a text box that is configured with type="number". A text box
  .text property either returns a Float or it returns an empty string
  """
  val = tb_control.text
  return val if type(val) is float else 0.0

def active_client_name():
  """Returns the name of the currently active client, if there is one. 
  Returns empty string otherwise.
  """
  cur_user = get_user()
  if cur_user:
    last_client_id = cur_user['last_client_id']
    if last_client_id:
      return chg_none(anvil.server.call('get_client', last_client_id)['full_name'], '')
