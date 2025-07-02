from ._anvil_designer import PDF_GenTemplate
from anvil import *
import anvil.server
import anvil.users
from ..Pages import PDF_Gen_mod

client_name = 'Niko Gessner'
client_address = '11100 Stony Brook Dr'
ahs_id = '123'
assessor = 'Jane Austen'
date = '12/13/23'

#home desctiption info
square_footage = '200000'
year_built = '1354'
heating_system = "Gas Stove"
current_annual_heating_cost = '204'
domestic_hot_water = 'Heater Tank'
electrical_service = 'Chugach'

# heat pump options
option= 'Air souirce heat pump'
heat_pump_installation_cost = '2000'
tax_credits = '400'
total_heat_pump_cost = '2300'
total_cost = '345890'
electricy_cost_change = '34'
net_annual_savings= '234'
percent_reduction = '34'
payback = '3'
remaining_oil_usage = 34
avoided_co2 = '34'

#if different than assessor
ahs_energy_advisor= 'Shakespeare'

heat_pump_1 = ['option 1', 2000,12,23,34,45,56,67,78,89,90]
heat_pump_2 = ['option 2', 3000,12,23,34,45,56,67,78,89,90]


class PDF_Gen(PDF_GenTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.


  def button_1_click(self, **event_args):
    """This method is called when the component is clicked."""
    """This method is called when the button is clicked"""

    pdf = PDF_Gen_mod.AkHeatSmartPDF(client_name, client_address, ahs_id, 
                                     assessor, date, square_footage, year_built,
                                     heating_system, current_annual_heating_cost,
                                     domestic_hot_water, electrical_service,
                                     heat_pump_1,heat_pump_2)
    anvil.media.download(pdf)
    pass
