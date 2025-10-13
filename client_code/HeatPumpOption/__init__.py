from ._anvil_designer import HeatPumpOptionTemplate
from anvil import *
import anvil.server
import m3.components as m3
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Utility import chg_none

class HeatPumpOption(HeatPumpOptionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def recalc_cost_totals(self, **event_args):
    """This method is called when the text in this component is edited."""
    try:
      print(self.text_box_cost_hp_install.text)
      print(self.text_box_cost_electrical.text)
      print(chg_none(self.text_box_cost_electrical.text, 0))
      print(float(chg_none(self.text_box_cost_hp_install.text, 0)))
      sys_cost = chg_none(self.text_box_cost_hp_install.text, 0) + \
          float(chg_none(self.text_box_cost_electrical.text, 0)) + \
          float(chg_none(self.text_box_cost_permit.text, 0))
      self.text_system_cost.text = f'${sys_cost:,.0f}'
    except Exception as e:
      print(e)
      self.text_system_cost.text = ''
