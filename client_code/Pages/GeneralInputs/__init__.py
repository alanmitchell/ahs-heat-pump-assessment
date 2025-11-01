import copy

from ._anvil_designer import GeneralInputsTemplate
from anvil import *
import m3.components as m3
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.http
from anvil.users import get_user
from ...Utility import chg_none, active_client_name
from ...HeatPumpOption import HeatPumpOption
from ... import Library

class GeneralInputs(GeneralInputsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.general_inputs_link.selected = True
    self.set_event_handler("show", self.form_show)
    self.set_event_handler("hide", self.save_values)

    # load the Assessor dropdown
    self.dropdown_menu_assessor.items = [
      (u["full_name"], u["id"]) for u in anvil.server.call("get_users_public_fields")
    ]
    
    # get the client we are currently working on
    self.client_id = get_user()["last_client_id"]
    if self.client_id:
      fields = ('full_name', 'email', 'address', 'city', 'assessment_id', 'assessor', 'assess_visit_date')
      client = anvil.server.call('get_client', self.client_id, fields)
      client.pop('row_id')  # already have this as self.client_id
      assessor = client.pop('assessor')
      client['assessor_id'] = assessor.get_id() if assessor else None
      self.item = client
      self.dropdown_menu_assessor.selected_value = self.item['assessor_id']
      self.last_saved = copy.deepcopy(self.item)    # tracks last inputs saved
    else:
      self.last_saved = {}

  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f"**Client:** {active_client_name()}"

  def dropdown_menu_assessor_change(self, **event_args):
    """This method is called when an item is selected"""
    self.item['assessor_id'] = self.dropdown_menu_assessor.selected_value

  def save_values(self, **event_args):
    """Save inputs if they have changed."""
    if self.item != self.last_saved:
      anvil.server.call('add_update_client', self.client_id, self.item)
      print('Saved Values')
      self.last_saved = copy.deepcopy(self.item)
