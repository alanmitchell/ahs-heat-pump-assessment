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
    self.dropdown_menu_hp_source.items = Library.HEAT_PUMP_WATER_HEATER_SOURCE
    self.dropdown_menu_dhw_after_fuel.items = Library.FUELS_ALL
    self.dropdown_menu_unserved_source.items = Library.UNSERVED_HP_LOAD
    self.heating_system_unserved.visible = False

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
      self.dropdown_menu_hp_source.visible = (dhw_type == 'new-hpwh')
      self.text_hpwh_source.visible = (dhw_type == 'new-hpwh')
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
    """Updates data bindings (moves data from .item to the controls), 
    including dropdowns that aren't explicitly bound.
    """
    self.refresh_data_bindings()
    self.recalc_cost_totals()
    self.checkbox_split_unit_change()
    self.dropdown_menu_hp_source.selected_value = self.item.get('hp_source', None)
    self.dropdown_menu_hp_source_change()
    self.dropdown_menu_hp_distribution.selected_value = self.item.get('hp_distribution', None)
    self.dropdown_menu_hp_distribution_change()
    self.dropdown_menu_dhw_source.selected_value = self.item.get('dhw_source', None)
    self.dropdown_menu_dhw_source_change()
    self.dropdown_menu_dhw_after_fuel.selected_value = self.item.get('dhw_after_fuel', None)
    self.dropdown_menu_hpwh_source.selected_value = self.item.get('hpwh_source', None)
    self.update_inaccessible_load()
    self.dropdown_menu_unserved_source.selected_value = self.item.get('unserved_source', None)
    self.dropdown_menu_unserved_source_change()

    self.heating_system_unserved.item = self.item.get('heating_system_unserved', {}).copy()
    self.heating_system_unserved.refresh()

  def update_item_property(self):
    """Takes values from the custom controls and moves them to the item property
    of this control, since this data movement does not automatically occur when a change occurs
    in the custom control.
    """
    self.item['heating_system_unserved'] = self.heating_system_unserved.item.copy()

  def dropdown_menu_hp_source_change(self, **event_args):
    """HP Source type changed"""
    hp_source = self.dropdown_menu_hp_source.selected_value
    self.item['hp_source'] = hp_source
    self.text_box_hspf2.visible = (hp_source == 'air')
    self.text_rating_or.visible = (hp_source == 'air')
    if hp_source == 'air':
      self.text_box_cop32f.label = 'Realistic COP @ 32 °F Outside Air'
      self.text_max_capacity.text = 'Maximum Capacity at 5 °F Outside Air:'
    else:
      self.text_box_cop32f.label = 'Realistic COP @ 32 °F EWT'
      self.text_max_capacity.text = 'Maximum Capacity at 32 °F EWT:'

  def dropdown_menu_dhw_after_fuel_change(self, **event_args):
    """DHW Fuel after Heat Pump changed"""
    self.item['dhw_after_fuel'] = self.dropdown_menu_dhw_after_fuel.selected_value

  def dropdown_menu_hpwh_sourece_change(self, **event_args):
    self.item['hpwh_source'] = self.dropdown_menu_hpwh_source.selected_value

  def update_inaccessible_load(self, **event_args):
    """This method is called when the text in this component is edited."""
    inaccessible_load = 100.0 - text_to_float(self.text_box_load_exposed) - \
      text_to_float(self.text_box_load_adjacent)
    self.text_inaccessible_load.text = f'{inaccessible_load:,.1f}%'

  def dropdown_menu_unserved_source_change(self, **event_args):
    """This method is called when an item is selected"""
    unserved_source = self.dropdown_menu_unserved_source.selected_value
    self.item['unserved_source'] = unserved_source
    self.heating_system_unserved.visible = (unserved_source == 'other')

