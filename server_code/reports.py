import anvil.media
import anvil.server
from anvil.tables import app_tables

from jinja2 import Environment, FileSystemLoader, BaseLoader

from .dict2d import Dict2d
from .util import convert

# Map Calculator API Fuel ID to labels and units
FUEL_INFO = {
  "oil1": ('Oil', 'gallons', ',.0f'),
  "propane": ('Propane', 'gallons', ',.0f'),
  "elec": ('Electricity', 'kWh', ',.0f'),
  "birch": ('Birch', 'cords', ',.2f'),
  "spruce": ('Sprucce', 'cords', ',.2f'),
  "pellets": ('Wood Pellets', 'pounds', ',.0f'),
  "ng": ('Natural Gas', 'CCF', ',.0f'),
}

END_USE_LABELS = {
  'space_htg': 'Space Heating',
  'dhw': 'Domestic Hot Water',
  'cooking': 'Cooking',
  'drying': 'Clothes Drying',
  'misc_elec': 'Miscellaneous Electric',
  'ev_charging': 'EV Charging',
  'pv_solar': 'PV Solar',
}

def make_retrofit_report(analyze_results):
  """Returns a Markdown string with the report contents resulting from the 
  Heat Pump analysis. 'analyze_results' is a dictionary containing a calculation success
  flag, error messages if the calculation couldn't be performed, or the analysis results
  dictionary if the calculation was successful.
  """
  env = Environment(
    loader=BaseLoader(),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,  # appropriate for Markdown
  )

  if analyze_results['success']:
    # Report for a successful retrofit analysis
    data = {}
    ar = analyze_results['results']    # shortcut variable

    # ---------- Make the model fitting statistics table
    tbl_fit = []
    for fuel_id, info in ar['fuel_fit_info'].items():
      label, units, fmt = FUEL_INFO[fuel_id]
      tbl_fit.append(
        (
          f'{label}, {units}',
          f'{info[0]:{fmt}}',
          f'{info[1]:{fmt}}',
          f'{info[2]*100:.1f}%'
        )
      )
    data['tbl_fit'] = tbl_fit

    # --------- Table of fuel use by End Use and total $ by Fuel
    # Get the 2-level dictionary that have fuel by end-use expressed in fuel
    # units.
    fuel_by_use = Dict2d(ar['existing_results']['annual_results']['fuel_use_units'])
    fuels = fuel_by_use.key1_list()
    end_uses = fuel_by_use.key2_list()
    
    # make the header row
    tbl_fuel_by_use_header = ['End Use'] + [f'{FUEL_INFO[fuel][0]}, {FUEL_INFO[fuel][1]}' for fuel in fuels]
    data['tbl_fuel_by_use_header'] = tbl_fuel_by_use_header
    
    tbl_fuel_by_use = []
    for end_use in end_uses:
      row = [END_USE_LABELS[end_use]]
      row += [convert(f'{fuel_by_use.get(fuel, end_use):{FUEL_INFO[fuel][2]}}', ('0', '0.0', '0.00'), '') for fuel in fuels]
      tbl_fuel_by_use.append(row)
    data['tbl_fuel_by_use'] = tbl_fuel_by_use
    
    # get the totals by fuel type
    fuel_totals = fuel_by_use.sum_key1()
    data['tbl_fuel_by_use_totals'] = ['Totals'] + [f'{fuel_totals.get(fuel, 0.0):{FUEL_INFO[fuel][2]}}' for fuel in fuels]

    # get the cost totals by fuel type
    fuel_cost_by_type = ar['existing_results']['annual_results']['fuel_cost']
    data['tbl_fuel_by_use_total_cost'] = ['Total Fuel Cost'] + [f'$ {fuel_cost_by_type.get(fuel, 0.0):,.0f}' for fuel in fuels]
    
    template_text = app_tables.settings.search(key="analyze-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(**data)

  else:
    # Display input error messages
    template_text = app_tables.settings.search(key="error-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(messages=analyze_results['messages'])
