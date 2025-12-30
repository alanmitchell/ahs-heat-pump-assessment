"""Module for managing the interface to the backend Calculator API. Prepares inputs
from the UI to be used in the Heat Pump Calculator API.
"""
import json

import requests
from pprint import pprint
import anvil.server

from .client_data import get_client
from .past_fuel_use import get_actual_use
from .ui_to_api import make_base_bldg_inputs, make_energy_model_fit_inputs

# Base URL to access heat pump calculator API endpoints.
CALCULATOR_API_BASE_URL = "https://heatpump-api.energytools.com/"

@anvil.server.callable
def calculator_api_base_url():
  return CALCULATOR_API_BASE_URL

def return_errors(error_messages):
  """Returns the results dictionary used to convey that an error(s) has occurred.
  'error_messages' is a list of error messages.
  """
  return {
    "success": False,
    "messages": error_messages,
  }

@anvil.server.callable
def analyze_options(ui_inputs, client_id):
  """Performs the full analysis of all heat pump options and As Installed case.
  'input_dict': The dictionary of all the model inputs.
  'client_id': The ID of the client being modeled.
  """
  #anvil.server.call('pprint', ui_inputs)

  # ----- Get the client record with needed fields
  fields = ('historical_use_file_id', )
  client = get_client(client_id, fields)

  # ----- Validate the inputs before doing calculations
  err_msgs = []
  # Acquire actual fuel use and capture errors.
  if client['historical_use_file_id']:
    try:
      actual_fuel_use = get_actual_use(client['historical_use_file_id'])
    except Exception as e:
      err_msgs.append(f"There are Data problems in the Historical Fuel Use Spreadsheet:\n{e}")
  else:
    err_msgs.append('The Historical Fuel Use Spreadsheet has not been created.')

  if err_msgs:
    return return_errors(err_msgs)

  # ----- Make the API inputs for the base, existing building
  base_bldg_api_inputs = make_base_bldg_inputs(ui_inputs)

  # ----- Fit the inputs to actual fuel use.
  fit_inputs = make_energy_model_fit_inputs(base_bldg_api_inputs, actual_fuel_use)
  fit_results = requests.post(
    CALCULATOR_API_BASE_URL + 'energy/fit-model',
    json=fit_inputs,
    timeout = 30,
  )
  if fit_results.status_code >= 400:
    err = fit_results.json()
    try:
      err_msg = f"{err['detail']} {err['timestamp']}"
    except:
      err_msg = str(err)
    err_msgs.append(err_msg)
    return return_errors(err_msgs)

  pprint(fit_results.json())
  return {'success': True, 'messages': []}
