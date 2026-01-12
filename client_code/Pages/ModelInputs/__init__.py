import copy

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

# Report message shown when there are no fresh results.
NO_RESULTS_MSG = '<h2>No Results Yet. Click Calculate button above.</h2>'

class ModelInputs(ModelInputsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.model_inputs_link.selected = True
    self.set_event_handler('show', self.form_show)
    self.set_event_handler('hide', self.save_values)

    self.html_report = HtmlTemplate()
    self.html_report.html = NO_RESULTS_MSG
    self.card_content_container.add_component(self.html_report)

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

    # initial visibility of heating system tabs
    self.heating_system_primary.visible = True
    self.heating_system_secondary.visible = False

    # DHW Inputs
    self.dropdown_menu_dhw_sys_type.items = Library.DHW_SYS_TYPES
    self.dropdown_menu_dhw_fuel.items = Library.FUELS_ALL
    self.dropdown_menu_hpwh_source.items = Library.HEAT_PUMP_WATER_HEATER_SOURCE

    # Fuels for Cooking Clothes Drying
    self.dropdown_menu_cooking_fuel.items = Library.FUELS_DRYING_COOKING
    self.dropdown_menu_drying_fuel.items = Library.FUELS_DRYING_COOKING
    
    # Load heat pump options
    self.heat_pump_options = []
    for i in range(4):
      option = HeatPumpOption()
      option.visible = True if i == 0 else False
      self.heat_pump_options.append(option)
      self.card_content_container_hp_options.add_component(option)

    # get the client we are currently working on
    self.client_id = get_user()["last_client_id"]
    if self.client_id:
      fields = ('model_inputs', 'version_model_inputs')
      client = anvil.server.call('get_client', self.client_id, fields)
      if client:
        # Get rid of row_id as it will affect Inputs changed comparison
        client.pop('row_id')
        self.last_saved = copy.deepcopy(client)   # used to determine if inputs have changed
      else:
        self.last_saved = {}
        
      if client['model_inputs']:
        # Item property only holds the model inputs, not version_model_inputs
        self.item = client['model_inputs'] 
      else:
        # put default values here
        self.item = {'primary_residence': True}

      # Fill out components that are not explicitly bound.
      # *** REMEMBER to manually call Change, Enter, Lost Focus Events
      inp = self.item     # shortcut
      # modeling city. It's an ID in input dictionary, not a text string
      rev_city_map = {v: k for k, v in self.city_map.items()}
      model_city_id = inp.get('model_city', None)
      if model_city_id is not None:
        self.autocomplete_model_city.text = rev_city_map[model_city_id]
        self.autocomplete_model_city_change()   # force event to fire
      self.dropdown_menu_rate_sched.selected_value = inp.get('rate_sched', None)
      self.dropdown_menu_garage_count.selected_value = str(inp.get('garage_count', 0))
      self.dropdown_menu_dhw_sys_type.selected_value = inp.get('dhw_sys_type', None)
      self.dropdown_menu_dhw_sys_type_change()
      self.dropdown_menu_dhw_fuel.selected_value = inp.get('dhw_fuel', None)
      self.dropdown_menu_hpwh_source.selected_value = inp.get('hpwh_source', None)
      self.dropdown_menu_cooking_fuel.selected_value = inp.get('cooking_fuel', None)
      self.dropdown_menu_drying_fuel.selected_value = inp.get('drying_fuel', None)

      # heating systems
      self.heating_system_primary.item = inp.get('heating_system_primary', {}).copy()
      self.heating_system_primary.refresh()
      self.heating_system_secondary.item = inp.get('heating_system_secondary', {}).copy()
      self.heating_system_secondary.refresh()
      
      # heat pump options
      default_options = [{} for i in range(len(self.heat_pump_options))]
      default_options[-1]['title'] = 'As Installed'
      options = inp.get('heat_pump_options', default_options)
      i = 0
      for option in options:
        self.heat_pump_options[i].item = option.copy()
        self.heat_pump_options[i].refresh()
        i += 1
        
    else:
      self.last_saved = {}
  
  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f'**Client:** {active_client_name()}'

  def autocomplete_model_city_change(self, **event_args):
    # if the change results in a valid city, populate the fuel price inputs
    # and the Electric Utility choices
    if self.autocomplete_model_city.text in self.city_map.keys():
      # lookup info for the city.
      city_id = self.city_map[self.autocomplete_model_city.text]
      self.item['model_city'] = city_id
      city = anvil.http.request(
        self.calc_api_url + f'lib/cities/{city_id}',
        method="GET",
        json=True
      )
      oil_price = city['Oil1Price'] or city['Oil2Price']    # No. 1 oil has preference
      self.text_box_oil_price.label = f'${oil_price:.2f} / gallon' if oil_price else 'NA / gallon'
      self.text_box_propane_price.label = f"${city['PropanePrice']:.2f} / gallon" if city['PropanePrice'] else 'NA / gallon'
      self.text_box_ng_price.label = f"${city['GasPrice']:.3f} / ccf" if city['GasPrice'] else 'NA / ccf'
      self.text_box_birch_price.label = f"${city['BirchPrice']:.0f} / cord" if city['BirchPrice'] else 'NA / cord'
      self.text_box_spruce_price.label = f"${city['SprucePrice']:.0f} / cord" if city['SprucePrice'] else 'NA / cord'
      self.text_box_pellet_price.label = f"${city['WoodPelletsPrice']:.3f} / pound" if city['WoodPelletsPrice'] else 'NA / pound'

      # Populate Electric Utility dropdown
      choices = [(util['label'], util['id']) for util in city['ElecUtilities'] if 'Resid' in util['label']]
      self.dropdown_menu_rate_sched.items = choices
      if len(choices):
        # select the first choice
        self.dropdown_menu_rate_sched.selected_value = choices[0][1]
      else:
        self.dropdown_menu_rate_sched.selected_value = None

    else:
      self.item['model_city'] = None
      # clear out rate schedule dropdown; otherwise it will retain the choices from the last
      # valid city.
      self.dropdown_menu_rate_sched.items = []
      self.dropdown_menu_rate_sched.selected_value = None

    # Need to fire change event so new Rate Sched selected value is stored
    self.dropdown_menu_rate_sched_change()

  def tabs_heating_system_tab_click(self, tab_index, tab_title, **event_args):
    """This method is called when a heating system tab is clicked"""
    if tab_index == 0:
      self.heating_system_primary.visible = True
      self.heating_system_secondary.visible = False
    else:
      self.heating_system_primary.visible = False
      self.heating_system_secondary.visible = True

  def tabs_hp_options_tab_click(self, tab_index, tab_title, **event_args):
    """This method is called when a Heat Pump Options tab is clicked"""
    for i in range(len(self.heat_pump_options)):
      self.heat_pump_options[i].visible = True if i == tab_index else False

  def dropdown_menu_dhw_sys_type_change(self, **event_args):
    """DHW System Type changed"""
    def controls(visibility=True, fuel_enabled=True):
      self.dropdown_menu_dhw_fuel.visible = visibility
      self.text_dhw_fuel.visible = visibility
      self.text_ef_dhw.visible = visibility
      self.text_box_ef_dhw.visible = visibility
      self.dropdown_menu_hpwh_source.visible = (sys_type == 'hpwh')
      self.text_hpwh_source.visible = (sys_type == 'hpwh')
      self.dropdown_menu_dhw_fuel.enabled = fuel_enabled
    sys_type = self.dropdown_menu_dhw_sys_type.selected_value
    self.item['dhw_sys_type'] = sys_type
    if sys_type == "from-space-htr" or sys_type is None:
      # set fuel to None; eventually pull fuel from Primary Space Heater
      self.dropdown_menu_dhw_fuel.selected_value = None
      self.dropdown_menu_dhw_fuel_change()
      controls(False)
    elif sys_type == "hpwh":
      self.dropdown_menu_dhw_fuel.selected_value = "elec"
      self.dropdown_menu_dhw_fuel_change()
      controls(True, False)
    else:
      controls()

  def dropdown_menu_garage_count_change(self, **event_args):
    self.item['garage_count'] = int(self.dropdown_menu_garage_count.selected_value)

  def dropdown_menu_rate_sched_change(self, **event_args):
    self.item['rate_sched'] = self.dropdown_menu_rate_sched.selected_value

  def dropdown_menu_dhw_fuel_change(self, **event_args):
    self.item['dhw_fuel'] = self.dropdown_menu_dhw_fuel.selected_value

  def dropdown_menu_hpwh_source_change(self, **event_args):
    self.item['hpwh_source'] = self.dropdown_menu_hpwh_source.selected_value

  def dropdown_menu_cooking_fuel_change(self, **event_args):
    self.item['cooking_fuel'] = self.dropdown_menu_cooking_fuel.selected_value

  def dropdown_menu_drying_fuel_change(self, **event_args):
    self.item['drying_fuel'] = self.dropdown_menu_drying_fuel.selected_value

  def transfer_values_from_custom_comps(self):
    """Transfers values from custom compoentns to the main item dictionary
    of this form."""
    self.item['heating_system_primary'] = self.heating_system_primary.item.copy()
    self.item['heating_system_secondary'] = self.heating_system_secondary.item.copy()
    
    # first ensure that item property of Option custom controls are up-to-date
    [option.update_item_property() for option in self.heat_pump_options]
    options = [option.item.copy() for option in self.heat_pump_options]
    self.item['heat_pump_options'] = options

  def save_values(self, **event_args):
    # If inputs have changed, save them to the Server DataTable.
    # add the model inputs version both to the model inputs dictionary and the 
    # main record.
    self.transfer_values_from_custom_comps()
    self.item['version_model_inputs'] = Library.VERSION_MODEL_INPUTS
    client_rec = {'version_model_inputs': Library.VERSION_MODEL_INPUTS, 'model_inputs': self.item}
    if client_rec != self.last_saved:
      self.html_report.html = NO_RESULTS_MSG
      anvil.server.call('add_update_client', self.client_id, client_rec)
      print('Saved Values')
      self.last_saved = copy.deepcopy(client_rec)

  def button_calculate_click(self, **event_args):
    """This method is called when the component is clicked."""
    self.html_report.html = '<h2>Calculating!</h2>'
    self.save_values()
    report_html = anvil.server.call('analyze_options', self.item, self.client_id)
    self.html_report.html = report_html
