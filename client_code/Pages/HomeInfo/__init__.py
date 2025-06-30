from ._anvil_designer import HomeInfoTemplate
from anvil import *
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class HomeInfo(HomeInfoTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    #self.layout.deselect_all_nav_links()
    self.layout.home_info_link.selected = True