from ._anvil_designer import HeatingSystemTemplate
from anvil import *
import anvil.server
import m3.components as m3
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Library import FUELS_ALL

class HeatingSystem(HeatingSystemTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.dropdown_menu_fuel.items = FUELS_ALL
