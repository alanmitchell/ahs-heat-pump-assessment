from ._anvil_designer import HeatPumpOptionTemplate
from anvil import *
import anvil.server
import m3.components as m3
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Utility import text_to_float
from .. import Library

class HeatPumpOption(HeatPumpOptionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.dropdown_menu_dhw_source.items = Library.DHW_AFTER_HP
    self.dropdown_menu_dhw_after_fuel.items = Library.FUELS_ALL

  def recalc_cost_totals(self, **event_args):
    """This method is called when the text in this component is edited."""
    #try:
    sys_cost = text_to_float(self.text_box_cost_hp_install) + \
      text_to_float(self.text_box_cost_electrical) + \
      text_to_float(self.text_box_cost_permit)
    self.text_system_cost.text = f'${sys_cost:,.0f}'
    total_cost = sys_cost + text_to_float(self.text_box_cost_non_hp) - \
      text_to_float(self.text_box_hp_incentives) - text_to_float(self.text_box_hp_tax_credit)
    self.text_total_cost.text = f'${total_cost:,.0f}'

  def dropdown_menu_dhw_source_change(self, **event_args):
    """Determine whether more info is needed."""
    dhw_type = self.dropdown_menu_dhw_source.selected_value
    if dhw_type in (3, 4, 5):
      self.grid_panel_new_dhw.visible = True
      if dhw_type == 5:
        self.dropdown_menu_dhw_after_fuel.selected_value = 1
        self.dropdown_menu_dhw_after_fuel.enabled = False
      else:
        self.dropdown_menu_dhw_after_fuel.enabled = True

    else:
      self.grid_panel_new_dhw.visible = False
