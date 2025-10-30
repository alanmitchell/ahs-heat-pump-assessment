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

  def refresh(self):
    """Moves values fromm item property to the controls.
    """
    self.dropdown_menu_fuel.selected_value = self.item.get('fuel', None)
    self.dropdown_menu_fuel_change()   # need to fire Change event
    self.dropdown_menu_system_type.selected_value = self.item.get('system_type', None)
    self.refresh_data_bindings()

  def dropdown_menu_fuel_change(self, **event_args):
    """Populate System Types based on Fuel"""
    fuel_id = self.dropdown_menu_fuel.selected_value
    self.item['fuel'] = fuel_id
    if fuel_id is not None:
      self.dropdown_menu_system_type.items = Library.SPACE_HTG_SYS_TYPES[fuel_id]

  def dropdown_menu_system_type_change(self, **event_args):
    """This method is called when an item is selected"""
    self.item['system_type'] = self.dropdown_menu_system_type.selected_value

  def pct_load_change(self, **event_args):
    self.raise_event("x-pct-load-change", value=self.text_box_pct_load_served.text, sender=self, **event_args)
