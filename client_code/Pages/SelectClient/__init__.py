from ._anvil_designer import SelectClientTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import State

class SelectClient(SelectClientTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.select_client_link.selected = True
    self.repeating_panel_select_client.set_event_handler("x-row-selected", self.row_selected)

    self.all_clients = [user for user in anvil.server.call('get_users_public_fields') if user['is_staff']==False]
    self.repeating_panel_select_client.items = self.all_clients

    # find the target client and display email and name
    # default to first client in case target client is not there
    target_client = self.all_clients[0] if len(self.all_clients) else None
    # this is the client we'd like to find
    target_id = State.target_user_id
    for client in self.all_clients:
      if client['id'] == target_id:
        target_client = client
        break
    if target_client:     # may be None
      self.rich_text_selected_client.content = f"Currently Selected Client: **{target_client['email']}, {target_client['full_name']}**"

  def text_box_search_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    query = self.text_box_search.text.strip().lower()
    self.repeating_panel_select_client.items = [
      u for u in self.all_clients
      if query in u['email'].lower() or query in u['full_name'].lower()
    ]

  def row_selected(self, item, **event_args):
    self.rich_text_selected_client.content = f"Currently Selected Client: **{item['email']}, {item['full_name']}**"
    State.target_user_id = item['id']
    # for this staff user, remember this ID so when they come back they don't have to reselect
    # a client
    anvil.server.call('update_user_info_by_staff', State.current_user.get_id(), {'last_client_id': item['id']})
