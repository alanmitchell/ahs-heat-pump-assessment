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
      client = anvil.server.call('get_client', client_id)
      historical_file_id = client['historical_use_file_id']  # file id of historical use spreadsheet
      if historical_file_id is None:
        # No spreadsheet created yet, so make one
        client_name = client['full_name'] if client['full_name'] else "Unknown"
        d = anvil.js.window.Date()
        timestamp_str = f"{d.getFullYear()}-{d.getMonth()+1:02d}-{d.getDate():02d} {d.getHours():02d}:{d.getMinutes():02d}"
        historical_file_id = anvil.server.call('make_client_historical_use_ss', f"{client_name} Historical Use {timestamp_str}")
        # save the file ID in the DataTable
        anvil.server.call('update_client', client['row_id'], {'historical_use_file_id': historical_file_id})
      url = f"https://docs.google.com/spreadsheets/d/{historical_file_id}/edit"
      anvil.js.window.open(url, "_blank")
      
    else:
      alert("There is no Selected Client!")

  def but_import_historical_use_click(self, **event_args):
    """This method is called when the component is clicked."""
    self.text_historical_use.text = anvil.server.call()
