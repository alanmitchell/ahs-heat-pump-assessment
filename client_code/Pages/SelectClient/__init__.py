from ._anvil_designer import SelectClientTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SelectClient(SelectClientTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.select_client_link.selected = True
    self.repeating_panel_select_client.set_event_handler("x-row-selected", self.row_selected)

    self.all_users = anvil.server.call('get_users_public_fields')
    self.repeating_panel_select_client.items = self.all_users

  def text_box_search_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    query = self.text_box_search.text.strip().lower()
    self.repeating_panel_select_client.items = [
      u for u in self.all_users
      if query in u['email'].lower() or query in u['name'].lower()
    ]

  def row_selected(self, item, **event_args):
    alert(f"Selected: {item['email']}")
