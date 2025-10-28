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

    # get the client we are currently working on
    self.client_id = get_user()["last_client_id"]

    # load the Assessor dropdown
    self.dropdown_menu_assessor.items = [
      (u["full_name"], u["id"]) for u in anvil.server.call("get_users_public_fields")
    ]

  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f"**Client:** {active_client_name()}"

