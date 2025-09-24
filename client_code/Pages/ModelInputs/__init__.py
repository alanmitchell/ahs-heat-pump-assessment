from ._anvil_designer import ModelInputsTemplate
from anvil import *
import m3.components as m3
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

    # load the modeling city Autocomplete Text box with suggestions.
    resp = anvil.http.request(
      self.calc_api_url + 'lib/cities',
      method="GET",
      json=True
    )
    # this will contain tuples of city, city_ID , sorted by city
    city_list = [rec['label'] for rec in resp]
    self.autocomplete_model_city.suggestions = city_list
    self.autocomplete_model_city.suggest_if_empty = True
    self.autocomplete_model_city.filter_mode = 'startswith'

    # also make a dictionary to map city name to it's ID
    self.city_map = {item['label']: item['id'] for item in resp}

    # load the Assessor dropdown
    self.dropdown_menu_assessor.items = [(u['full_name'], u['id']) for u in anvil.server.call("get_users_public_fields")]

  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f'**Client:** {active_client_name()}'

  def autocomplete_model_city_change(self, **event_args):
    # if the change results in a valid city, populate the fuel price inputs
    if self.autocomplete_model_city.text in self.city_map.keys():
    # lookup info for the city.
      city_id = self.city_map[self.autocomplete_model_city.text]
      city = anvil.http.request(
        self.calc_api_url + f'lib/cities/{city_id}',
        method="GET",
        json=True
      )
      self.text_box_oil_price.text = city['Oil1Price'] or city['Oil2Price']
      self.text_box_propane_price.text = city['PropanePrice']
      self.text_box_ng_price.text = '%.2f' % city['GasPrice'] if city['GasPrice'] else None
      self.text_box_birch_price.text = city['BirchPrice']
      self.text_box_spruce_price.text = city['SprucePrice']

      
    
