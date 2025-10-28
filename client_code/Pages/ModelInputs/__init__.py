from ._anvil_designer import ModelInputsTemplate
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

class ModelInputs(ModelInputsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.model_inputs_link.selected = True
    self.set_event_handler('show', self.form_show)

    # get the client we are currently working on
    self.client_id = get_user()["last_client_id"]
    
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

    # initial visibility of heating system tabs
    self.heating_system_primary.visible = True
    self.heating_system_primary.text_box_pct_load_served.text = '100'
    self.heating_system_secondary.visible = False
    self.heating_system_secondary.text_box_pct_load_served.enabled = False

    # DHW System Type
    self.dropdown_menu_dhw_sys_type.items = Library.DHW_SYS_TYPES
    self.dropdown_menu_dhw_fuel.items = Library.FUELS_ALL

    # Fuels for Cooking Clothes Drying
    self.dropdown_menu_cooking_fuel.items = Library.FUELS_DRYING_COOKING
    self.dropdown_menu_drying_fuel.items = Library.FUELS_DRYING_COOKING
    
    # Load heat pump options
    self.heat_pump_options = []
    for i in range(3):
      option = HeatPumpOption()
      option.visible = True if i == 0 else False
      self.heat_pump_options.append(option)
      self.card_content_container_hp_options.add_component(option)

    # The dictionary that holds general inputs and model inputs from this form.
    # The inputs are split into two dictionaries: one holds general values that get a 
    # dedicated field in the Client table, and the other holds detailing modeling inputs.
    self.general_inputs = {}
    self.model_inputs = {}
    # Track the timestamp of the last time inputs were saved
    self.last_save_general = 0.0
    self.last_save_model = 0.0
  
  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f'**Client:** {active_client_name()}'

  def autocomplete_model_city_change(self, **event_args):
    # if the change results in a valid city, populate the fuel price inputs
    # and the Electric Utility choices
    if self.autocomplete_model_city.text in self.city_map.keys():
      # save the input
      self.save_model_inputs()
      # lookup info for the city.
      city_id = self.city_map[self.autocomplete_model_city.text]
      city = anvil.http.request(
        self.calc_api_url + f'lib/cities/{city_id}',
        method="GET",
        json=True
      )
      oil_price = city['Oil1Price'] or city['Oil2Price']   # No. 1 oil has preference
      self.text_box_oil_price.text = '%.2f' % oil_price if oil_price else None
      self.text_box_propane_price.text = '%.2f' % city['PropanePrice'] if city['PropanePrice'] else None
      self.text_box_ng_price.text = '%.2f' % city['GasPrice'] if city['GasPrice'] else None
      self.text_box_birch_price.text = city['BirchPrice']
      self.text_box_spruce_price.text = city['SprucePrice']

      # Populate Electric Utility dropdown
      choices = [(util['label'], util['id']) for util in city['ElecUtilities']]
      self.dropdown_menu_rate_sched.items = choices

  def tabs_heating_system_tab_click(self, tab_index, tab_title, **event_args):
    """This method is called when a heating system tab is clicked"""
    if tab_index == 0:
      self.heating_system_primary.visible = True
      self.heating_system_secondary.visible = False
    else:
      self.heating_system_primary.visible = False
      try:
        pct_primary = float(self.heating_system_primary.text_box_pct_load_served.text)
        self.heating_system_secondary.text_box_pct_load_served.text = str(100 - pct_primary)
      except:
        self.heating_system_secondary.text_box_pct_load_served.text = '0'
      self.heating_system_secondary.visible = True

  def tabs_hp_options_tab_click(self, tab_index, tab_title, **event_args):
    """This method is called when a Heat Pump Options tab is clicked"""
    for i in range(3):
      self.heat_pump_options[i].visible = True if i == tab_index else False

  def dropdown_menu_dhw_sys_type_change(self, **event_args):
    """DHW System Type changed"""
    def controls(visibility=True, fuel_enabled=True):
      self.dropdown_menu_dhw_fuel.visible = visibility
      self.text_dhw_fuel.visible = visibility
      self.text_ef_dhw.visible = visibility
      self.text_box_ef_dhw.visible = visibility
      self.dropdown_menu_dhw_fuel.enabled = fuel_enabled

    if self.dropdown_menu_dhw_sys_type.selected_value == 1:
      controls(False)
    elif self.dropdown_menu_dhw_sys_type.selected_value == 4:
      self.dropdown_menu_dhw_fuel.selected_value = 1
      controls(True, False)
    else:
      controls()

  def save_general_inputs(self, **event_args):
    """Extracts general inputs from the Form and puts them into a dictionary. Sends that dictionary
    to the server to be stored in the ClientData table, one field per input. Stores no more frequently
    than every 5 seoncds.
    """

    # use a shortcut variable
    inp = self.general_inputs
    inp['full_name'] = self.text_box_full_name.text
    inp['address'] = self.text_box_address.text
    inp['city'] = self.text_box_city.text       # put modeling city in other dictionarry
    inp['assessment_id'] = self.text_box_assessment_id.text
    inp['assessor_id'] = self.dropdown_menu_assessor.selected_value
    inp['assess_visit_date'] = self.date_picker_visit_date.date
    print(inp)
    
  def save_model_inputs(self, **event_args):
    """Extracts model inputs from the Form and puts them in a dictionary. Sends that dictionary
    to the server to be stored in the ClientData table; the entire dictionary is stored in one
    field.
    """

    # Use a shortcut variable
    inp = self.model_inputs
    inp['model_city_id'] = self.city_map[self.autocomplete_model_city.text]
    print(inp)

    