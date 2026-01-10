import anvil.media
import anvil.server
from anvil.tables import app_tables

from jinja2 import Environment, FileSystemLoader, BaseLoader

from .dict2d import Dict2d
from .util import convert

# Map Calculator API Fuel ID to labels and units
FUEL_INFO = {
  "oil1": ('Oil', 'gallons'),
  "propane": ('Propane', 'gallons'),
  "elec": ('Electricity', 'kWh'),
  "birch": ('Birch', 'cords'),
  "spruce": ('Sprucce', 'cords'),
  "pellets": ('Wood Pellets', 'pounds'),
  "ng": ('Natural Gas', 'CCF'),
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

    # make the model fitting statistics table
    tbl_fit = []
    for fuel_id, info in ar['fuel_fit_info'].items():
      label, units = FUEL_INFO[fuel_id]
      tbl_fit.append(
        (
          f'{label}, {units}',
          f'{info[0]: ,.4g}',
          f'{info[1]: ,.4g}',
          f'{info[2]*100:.1f}%'
        )
      )
    data['tbl_fit'] = tbl_fit

    # Table of fuel use by End Use and total $ by Fuel
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
      row += [convert(f'{fuel_by_use.get(fuel, end_use):,.3g}', ('0',), '') for fuel in fuels]
      tbl_fuel_by_use.append(row)
    data['tbl_fuel_by_use'] = tbl_fuel_by_use

    print(data)
    template_text = app_tables.settings.search(key="analyze-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(**data)

  else:
    # Display input error messages
    template_text = app_tables.settings.search(key="error-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(messages=analyze_results['messages'])
