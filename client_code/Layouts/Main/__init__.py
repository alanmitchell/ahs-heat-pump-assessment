from ._anvil_designer import MainTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from anvil.js import window

# now window is the JS global, and your M3 namespace lives under window.m3
NavigationLink = window.m3.NavigationLink

class Main(MainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    print(self.layout.slots['navigation'])
    self._deselect_recursive(self.layout.slots['navigation'])

  def _deselect_recursive(self, container):
    print(container.get_components())
    for comp in container.get_components():
      print(comp)
      if isinstance(comp, NavigationLink):
        comp.selected = False
      if hasattr(comp, "get_components"):
        self._deselect_recursive(comp)