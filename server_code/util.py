import pprint as pretty
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
@anvil.server.callable
def pprint(obj):
  """Pretty prints 'obj' to the console.
  """
  pretty.pprint(obj)

def convert(value, match_list, replacement):
  '''If 'value' is in 'match_list', a Tuple or List, return 'replacement', otherwise return 'value'.
  '''
  return replacement if value in match_list else value
