import anvil.media
import anvil.server
from anvil.tables import app_tables

from jinja2 import Environment, FileSystemLoader, BaseLoader

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
    
    template_text = app_tables.settings.search(key="analyze-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(**data)

  else:
    # Display input error messages
    template_text = app_tables.settings.search(key="error-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(messages=analyze_results['messages'])
