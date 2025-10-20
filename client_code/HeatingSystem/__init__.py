from ._anvil_designer import HeatingSystemTemplate
from anvil import *
import anvil.server
import m3.components as m3
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Library

class HeatingSystem(HeatingSystemTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.dropdown_menu_fuel.items = Library.FUELS_ALL

  def dropdown_menu_fuel_change(self, **event_args):
    """Populate System Types based on Fuel"""
    fuel_id = self.dropdown_menu_fuel.selected_value
    self.dropdown_menu_system_type.items = Library.SPACE_HTG_SYS_TYPES[fuel_id]
