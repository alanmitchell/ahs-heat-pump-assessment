from ._anvil_designer import ModelInputsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.http
from ...Utility import chg_none, active_client_name

class ModelInputs(ModelInputsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.model_inputs_link.selected = True
    self.set_event_handler('show', self.form_show)

    # get base URL for Heatpump Calculator API
    self.calc_api_url = anvil.server.call('calculator_api_base_url')

    # load the modeling city dropdown.
    print(self.calc_api_url+ 'lib/cities')
    resp = anvil.http.request(
      self.calc_api_url + 'lib/cities',
      method="GET",
      json=True
    )
    print(resp)

  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f'**Client:** {active_client_name()}'
