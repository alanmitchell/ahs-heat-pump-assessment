"""Module for managing the interface to the backend Calculator API. Prepares inputs
from the UI to be used in the Heat Pump Calculator API.
"""
import anvil.server
import anvil.http

from .UI_to_API import make_base_bldg_inputs, make_energy_model_fit_inputs
from .Utility import convert

# Base URL to access heat pump calculator API endpoints.
CALCULATOR_API_BASE_URL = "https://heatpump-api.energytools.com/"

def return_errors(error_messages):
  """Returns the results dictionary used to convey that an error(s) has occurred.
  'error_messages' is a list of error messages.
  """
  return {
    "success": False,
    "messages": error_messages,
  }

def analyze_options(ui_inputs, client_id):
  """Performs the full analysis of all heat pump options and As Installed case.
  'input_dict': The dictionary of all the model inputs.
  'client_id': The ID of the client being modeled.
  """
  #anvil.server.call('pprint', ui_inputs)

  # ----- Get the client record with needed fields
  fields = ('historical_use_file_id',)
  client = anvil.server.call('get_client', client_id, fields)

  # ----- Validate the inputs before doing calculations
  err_msgs = []
  # Acquire actual fuel use and capture errors.
  if client['historical_use_file_id']:
    try:
      actual_fuel_use = anvil.server.call('get_actual_use', client['historical_use_file_id'])
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
  try:
    fit_results = anvil.http.request(
      CALCULATOR_API_BASE_URL + 'energy/fit-model',
      method="POST",
      data=fit_inputs,
      json=True
    )
  except anvil.http.HttpError as e:
    anvil.server.call('pprint', dir(e))
    err_msgs.append(str(e))
    return return_errors(err_msgs)

  anvil.server.call('pprint', fit_results)
  return {'success': True, 'messages': []}


def calculate_results(inputs):

  # Can enter the JSON below into Insomnium to debug
  #import json
  #print(json.dumps(inputs))  # will throw if not serializable

  try:
    resp = anvil.http.request(
      CALCULATOR_API_BASE_URL + 'energy/energy-model',
      method="POST",
      data=inputs,
      json=True
    )
  except anvil.http.HttpError as e:
    print(f"Error {e.status}")
    print(f"Error {e.content}")
    return {'status': e.status}

  return resp