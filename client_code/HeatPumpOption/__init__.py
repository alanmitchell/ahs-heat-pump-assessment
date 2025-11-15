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

    self.dropdown_menu_hp_source.items = Library.HP_SOURCE
    self.dropdown_menu_hp_distribution.items = Library.HP_HEAT_DISTRIBUTION
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
    self.item['dhw_source'] = dhw_type
    if dhw_type in ("new-tank", "new-tankless", "new-hpwh") :
      self.grid_panel_new_dhw.visible = True
      if dhw_type == "new-hpwh":
        self.dropdown_menu_dhw_after_fuel.selected_value = "elec"
        self.dropdown_menu_dhw_after_fuel.enabled = False
      else:
        self.dropdown_menu_dhw_after_fuel.enabled = True

    else:
      self.grid_panel_new_dhw.visible = False

  def dropdown_menu_hp_distribution_change(self, **event_args):
    """This method is called when an item is selected"""
    distrib = self.dropdown_menu_hp_distribution.selected_value
    self.item['hp_distribution'] = distrib
    self.checkbox_ducted.visible = (distrib == "air")

  def checkbox_split_unit_change(self, **event_args):
    """This method is called when the component is checked or unchecked"""
    if self.checkbox_split_unit.checked:
      self.text_number_heads.visible = True
      self.text_box_number_heads.visible = True
    else:
      self.text_number_heads.visible = False
      self.text_box_number_heads.visible = False

  def refresh(self):
    """Updates data bindings, including dropdowns that aren't explicitly bound.
    """
    self.refresh_data_bindings()
    self.recalc_cost_totals()
    self.checkbox_split_unit_change()
    self.dropdown_menu_hp_source.selected_value = self.item.get('hp_source', None)
    self.dropdown_menu_hp_distribution.selected_value = self.item.get('hp_distribution', None)
    self.dropdown_menu_hp_distribution_change()
    self.dropdown_menu_dhw_source.selected_value = self.item.get('dhw_source', None)
    self.dropdown_menu_dhw_source_change()
    self.dropdown_menu_dhw_after_fuel.selected_value = self.item.get('dhw_after_fuel', None)

  def dropdown_menu_hp_source_change(self, **event_args):
    """HP Source type changed"""
    self.item['hp_source'] = self.dropdown_menu_hp_source.selected_value

  def dropdown_menu_dhw_after_fuel_change(self, **event_args):
    """DHW Fuel after Heat Pump changed"""
    self.item['dhw_after_fuel'] = self.dropdown_menu_dhw_after_fuel.selected_value

  def update_inaccessible_load(self, **event_args):
    """This method is called when the text in this component is edited."""
    pass
