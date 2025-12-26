import time

from ._anvil_designer import PastFuelTemplate
from anvil import *
import m3.components as m3
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.users import get_user
import anvil.js

from ...Utility import active_client_name, chg_none_blank

class PastFuel(PastFuelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.past_use_link.selected = True
    self.set_event_handler('show', self.form_show)

  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f'**Client:** {active_client_name()}'

  def but_open_historical_ss_click(self, **event_args):
    """Open's historical use spreadsheet or creates & opens if one
    does not exist."""
    # get the client we are currently working on
    client_id = get_user()["last_client_id"]
    if client_id:
      client = anvil.server.call('get_client', client_id)
      historical_file_id = client['historical_use_file_id']  # file id of historical use spreadsheet
      if historical_file_id is None:
        # No spreadsheet created yet, so make one
        client_name = chg_none_blank(client['full_name'], "Unknown")
        assess_id = chg_none_blank(client['assessment_id'], 'Unknown')
        d = anvil.js.window.Date()
        timestamp_str = f"{d.getFullYear()}-{d.getMonth()+1:02d}-{d.getDate():02d} {d.getHours():02d}:{d.getMinutes():02d}"
        historical_file_id = anvil.server.call('make_client_historical_use_ss', f"{client_name} {assess_id} Historical Use {timestamp_str}")
        # save the file ID in the DataTable
        anvil.server.call('add_update_client', client['row_id'], {'historical_use_file_id': historical_file_id})
      url = f"https://docs.google.com/spreadsheets/d/{historical_file_id}/edit"
      anvil.js.window.open(url, "_blank")
      
    else:
      alert("There is no Selected Client!")

  def but_import_historical_use_click(self, **event_args):
    """This method is called when the component is clicked."""
    
    def set_default():
      self.rich_text_historical_use.content = "***No Historical Use Spreadsheet has been created!***"  # default if no data
    
    client_id = get_user()["last_client_id"]
    if client_id:
      client = anvil.server.call('get_client', client_id)
      historical_file_id = client['historical_use_file_id']  # file id of historical use spreadsheet
      if historical_file_id is not None:
        result = '|  |  |\n| --- | --- |\n'
        try:
          fuel_use =anvil.server.call('get_actual_use', historical_file_id)
          fuel_map = {
            'electricity_monthly': ('Monthly Electricity', 'kWh', ''),
            'oil_fills': ('Oil', 'gallons / year', '.0f'),
            'propane_fills': ('Propane', 'gallons / year', '.0f'),
            'ng_use': ('Natural Gas', 'ccf / year', '.0f'),
            'spruce_cords': ('Spruce', 'cords / year', '.2f'),
            'birch_cords': ('Birch', 'cords / year', '.2f'),
            'pellet_pounds': ('Wood Pellets', 'pounds / year', '.0f')
          }
          for var, val in fuel_use.items():
            label, units, fmt = fuel_map[var]
            result += f'| **{label}** | {val:{fmt}} {units} |\n'
          self.rich_text_historical_use.content = result
        except Exception as e:
          self.rich_text_historical_use.content = f"### There are Data problems in the Spreadsheet:\n\n{e}"
      else:
        set_default()
    else:
      set_default()

  def button_open_google_doc_click(self, **event_args):
    """Open's client's Google Document or creates & opens if one
    does not exist."""
    # get the client we are currently working on
    client_id = get_user()["last_client_id"]
    if client_id:
      client = anvil.server.call('get_client', client_id)
      google_doc_file_id = client['google_doc_file_id']  # file id of historical use spreadsheet
      if google_doc_file_id is None:
        # No spreadsheet created yet, so make one
        client_name = chg_none_blank(client['full_name'], "Unknown")
        assess_id = chg_none_blank(client['assessment_id'], 'Unknown')
        google_doc_file_id = anvil.server.call('make_client_google_doc', f"{client_name} {assess_id} Pictures/Misc")
        # save the file ID in the DataTable
        anvil.server.call('add_update_client', client['row_id'], {'google_doc_file_id': google_doc_file_id})
      url = f"https://docs.google.com/document/d/{google_doc_file_id}/edit"
      anvil.js.window.open(url, "_blank")

    else:
      alert("There is no Selected Client!")
