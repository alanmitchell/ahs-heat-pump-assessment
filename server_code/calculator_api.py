"""Module that access the Heat Pump Calculator API, which performs the core
heat pump performance and economics calculations.
"""
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# Base URL to access heat pump calculator API endpoints.
CALCULATOR_API_BASE_URL = "https://dolphin-app-jrrmh.ondigitalocean.app"

@anvil.server.callable
def calculator_api_base_url():
  return CALCULATOR_API_BASE_URL
