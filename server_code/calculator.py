"""Module for managing the interface to the backend Calculator API. Prepares inputs
from the UI to be used in the Heat Pump Calculator API.
"""
import json
import copy
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo
import time

import requests
from pprint import pprint
import anvil.server

from .calculator_constants import CALCULATOR_API_BASE_URL
from .client_data import get_client
from .past_fuel_use import get_actual_use
from .ui_to_api import (
  make_base_bldg_inputs,
  make_energy_model_fit_inputs, 
  make_option_building,
  make_econ_inputs,
  make_retrofit_cost,
)
from .util import convert
from .check_inputs import check_main_model_inputs
from .reports import make_retrofit_report

ALASKA_TZ = ZoneInfo("America/Anchorage")

def alaska_now_str() -> str:
  """Return current time in Alaska timezone as a string string."""
  return datetime.now(ALASKA_TZ).strftime("%Y-%m-%d %H:%M:%S AK Time")

def return_errors(error_messages):
  """Returns the results dictionary used to convey that an error(s) has occurred.
  'error_messages' is a list of error messages.
  """
  return make_retrofit_report({
    'success': False,
    'messages': error_messages
  })

@anvil.server.callable
def analyze_options(ui_inputs, client_id):
  """Performs the full analysis of all heat pump options and As Installed case.
  'input_dict': The dictionary of all the model inputs.
  'client_id': The ID of the client being modeled.
  """

  try:
    #x = 0 / 0
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
  
    # Check the main model inputs
    err_msgs = check_main_model_inputs(ui_inputs, actual_fuel_use)
    if err_msgs:
      return return_errors(err_msgs)
  
    # ----- Make the API inputs for the base, existing building
    base_bldg_api_inputs = make_base_bldg_inputs(ui_inputs)
  
    # ----- Fit the inputs to actual fuel use.
    fit_inputs = make_energy_model_fit_inputs(base_bldg_api_inputs, actual_fuel_use)
    fit_response = requests.post(
      CALCULATOR_API_BASE_URL + 'energy/fit-model',
      json=fit_inputs,
      timeout = 30,
    )
    if fit_response.status_code >= 400:
      err = fit_response.json()
      try:
        err_msg = f"{err['detail']} {err['timestamp']}"
      except:
        err_msg = str(err)
      err_msgs.append(err_msg)
      return return_errors(err_msgs)
  
    fit_results = fit_response.json()
    existing_bldg = fit_results['building_description']
    model_results = fit_results['model_results']
    existing_result = {
      'annual_results': model_results['annual_results'],
      'design_heat_temp': model_results['design_heat_temp'],
      'design_heat_load': model_results['design_heat_load']
    }
  
    # --- Do Retrofit analysis on each of the Options and the As Installed building
  
    # make the general economic inputs needed for the retrofit analysis
    econ_inputs = make_econ_inputs()
  
    # Holds modeling results from all options, or input error messages if option input
    # is not correct.
    option_results = []
    
    for option in ui_inputs['heat_pump_options']:
      option_bldg = make_option_building(existing_bldg, option)
      if type(option_bldg) is dict:
        # make retrofit cost inputs
        retrofit_cost = make_retrofit_cost(option)
        analyze_inputs = {
          'pre_bldg': existing_bldg,
          'post_bldg': option_bldg,
          'retrofit_cost': retrofit_cost,
          'economic_inputs': econ_inputs
        }
        analyze_response = requests.post(
          CALCULATOR_API_BASE_URL + 'energy/analyze-retrofit',
          json=analyze_inputs,
          timeout = 30,
        )
        if analyze_response.status_code >= 400:
          err = analyze_response.json()
          try:
            err_msg = f"{err['detail']} {err['timestamp']}"
          except:
            err_msg = str(err)
          err_msgs.append(err_msg)
          return return_errors(err_msgs)
  
        analyze_results = analyze_response.json()
        option_result = {
          'fuel_change': analyze_results['fuel_change'],
          'financial': analyze_results['financial'],
          'misc':  analyze_results['misc'],
          'annual_results': analyze_results['with_retrofit_detail']['annual_results'],
          'option_inputs': option
        }
        option_results.append(option_result)
  
      else:
        # 'option_bldg' is a string containing input error messages for this option
        option_results.append(option_bldg)
  
    # --- Report the Results
    final_results = {
      'fuel_fit_info': fit_results['fuel_fit_info'],
      'existing_results': existing_result,
      'option_results': option_results
    }  
      
    return make_retrofit_report({
        'success': True,
        'results': final_results
      })

  except Exception as exc:
    # Build full traceback string
    tb_str = "".join(
      traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    exc_time = alaska_now_str()
    print(f'{exc_time}: {tb_str}')
    msg = f'An Error occured in the Application at {exc_time}. Please report that time to the Developer.'  
    return_errors([msg,])