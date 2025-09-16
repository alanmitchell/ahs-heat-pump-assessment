from ._anvil_designer import SelectClientTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.users import get_user
from ...Utility import chg_none, chg_none_blank, active_client_name

class SelectClient(SelectClientTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.select_client_link.selected = True
    self.repeating_panel_select_client.set_event_handler("x-row-selected", self.row_selected)

    self.all_clients = anvil.server.call('get_clients')
    # substitute Assessor Name instead of full User DataTable row
    for client in self.all_clients:
      client['assessor'] = client['assessor']['full_name'] if client['assessor'] else 'No Assessor'
      client['assessment_id'] = chg_none_blank(client['assessment_id'], 'No ID')
      client['email'] = chg_none_blank(client['email'], 'No Email')
      client['full_name'] = chg_none_blank(client['full_name'], 'No Name')
    self.repeating_panel_select_client.items = self.all_clients

    # find the target client and display email and name
    # default to first client in case target client is not there
    target_client = self.all_clients[0] if self.all_clients is not None and len(self.all_clients) else None
    # this is the client we'd like to find
    target_id = get_user()['last_client_id']
    for client in self.all_clients:
      if client['row_id'] == target_id:
        target_client = client
        break
    if target_client:     # may be None
      self.layout.rich_text_client_name.content = f"**Client:** {target_client['full_name']}"
    self.set_event_handler('show', self.form_show)

  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f'**Client:** {active_client_name()}'
  
  def text_box_search_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    query = self.text_box_search.text.strip().lower()
    self.repeating_panel_select_client.items = [
      u for u in self.all_clients
      if query in u['email'].lower() or query in u['full_name'].lower() or query in u['assessment_id'].lower() or query in u['assessor'].lower()
    ]

  def row_selected(self, item, **event_args):
    self.layout.rich_text_client_name.content = f"**Client:** {item['full_name']}"
    anvil.server.call('update_user_info', {'last_client_id': item['row_id']})
