"""Utility functions.
"""

def chg_none(val, none_replacement=""):
  """Returns val unless it is None, whereupon it return 'none_replacement'.
  """
  return val if val is not None else none_replacement

