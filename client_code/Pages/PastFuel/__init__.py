from ._anvil_designer import PastFuelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class PastFuel(PastFuelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.past_use_link.selected = True

  def but_open_historical_ss_click(self, **event_args):
    """This method is called when the component is clicked."""
    new_file_id = anvil.server.call('make_client_historical_use_ss', )
