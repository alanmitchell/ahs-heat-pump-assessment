import anvil.media
import anvil.server
from anvil.tables import app_tables

from jinja2 import Environment, FileSystemLoader, BaseLoader

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
    ar = analyze_results    # shortcut variable

    # make the model fitting statistics table
    for fuel_id in ar[]
    
    template_text = app_tables.settings.search(key="analyze-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(**data)

  else:
    # Display input error messages
    template_text = app_tables.settings.search(key="error-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(messages=analyze_results['messages'])
