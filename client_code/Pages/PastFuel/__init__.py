import time

from ._anvil_designer import PastFuelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.users import get_user
import anvil.js

class PastFuel(PastFuelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.past_use_link.selected = True

  def but_open_historical_ss_click(self, **event_args):
    """This method is called when the component is clicked."""
    # get the client we are currently working on
    client_id = get_user()["last_client_id"]
    if client_id:
      client_info = anvil.server.call('get_client', client_id)
      client_name = client_info['full_name'] if client_info['full_name'] else "Unknown"
      new_file_id = anvil.server.call('make_client_historical_use_ss', f"{client_name} Historical Use {time.time():.0f}")
      url = f"https://docs.google.com/spreadsheets/d/{new_file_id}/edit"
      anvil.js.window.open(url, "_blank")
      
    else:
      alert("There is no Selected Client!")
