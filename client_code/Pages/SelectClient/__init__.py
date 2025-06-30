from ._anvil_designer import SelectClientTemplate
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SelectClient(SelectClientTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    #self.layout.deselect_all_nav_links()
    self.layout.select_client_link.selected = True
