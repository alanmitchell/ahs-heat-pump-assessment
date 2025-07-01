from ._anvil_designer import MainTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import m3.components as m3

class Main(MainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self._deselect_recursive(self.nav_panel)

  def _deselect_recursive(self, container):
    for comp in container.get_components():
      if isinstance(comp, m3.NavigationLink):
        comp.selected = False
      if hasattr(comp, "get_components"):
        self._deselect_recursive(comp)

  def select_client_link_click(self, **event_args):
    """This method is called when the component is clicked"""
    open_form('Pages.SelectClient')

  def home_info_link_click(self, **event_args):
    """This method is called when the component is clicked"""
    open_form('Pages.HomeInfo')

  def but_logout_click(self, **event_args):
    """This method is called when the component is clicked."""
    anvil.users.logout()
    open_form('Pages.Login')
