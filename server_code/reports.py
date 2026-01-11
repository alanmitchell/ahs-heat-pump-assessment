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
    tbl_fuel_by_use_header = ['End Use'] + [f'{FUEL_INFO[fuel][0]}<br>{FUEL_INFO[fuel][1]}' for fuel in fuels]
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

    # Grand total fuel cost and CO2 emissions
    data['grand_total_fuel_and_elec_cost'] = f"$ {ar['existing_results']['annual_results']['fuel_total_cost']:,.0f}"
    data['co2_lbs'] = f"{ar['existing_results']['annual_results']['co2_lbs']:,.0f}"

    # -------------- Heat Pump Options Table
    # identify the Options indices that actually contain results
    options = ar['option_results']
    option_indices = [ix for ix, val in enumerate(options) if type(val) is dict]
    tbl_options_header = [''] + [options[ix]['option_inputs']['title'] for ix in option_indices]
    data['tbl_options_header'] = tbl_options_header
    
    tbl_options = []
    def add_option_row(label, cell_function):
      row = [label] + [cell_function(ix) for ix in option_indices]
      tbl_options.append(row)

    # -- Fuel Use Change
    def fuel_change(i):
      lines = []
      for fuel, chg in options[i]['fuel_change']['units'].items():
        if chg != 0.0:
          name, units, fmt = FUEL_INFO[fuel]
          lines.append(f"{name}: {chg:+{fmt}} {units}")
      return '<br>'.join(lines)
    add_option_row('Annual Change in Fuel Use', fuel_change)          
        
    # -- Fuel Cost savings
    def cost_savings(i):
      savings = -sum(options[i]['fuel_change']['cost'].values())
      return f'$ {savings:,.0f}'
    add_option_row('First Year Energy Cost Savings', cost_savings)

    # -- CO2 Savings
    def co2_savings(i):
      return f"{options[i]['misc']['co2_lbs_saved']:,.0f}"
    add_option_row('CO2 Emissions Savings, lbs / year', co2_savings)

    # -- % of Space Load served by HP
    def pct_served(i):
      served = options[i]['annual_results']['hp_load_frac']
      return f'{served * 100.0:.0f}%'
    add_option_row('% Space Load served by Heat Pump', pct_served)

    # --Space Heating COP
    def cop(i):
      cop = options[i]['annual_results']['cop']
      return f'{cop:.2f}'
    add_option_row('Space Heating Heat Pump COP', cop)
    
    # -- Net Capital Cost
    def net_capital(i):
      capital_cost = -options[i]['financial']['cash_flow_table']['Net Cash'][0]
      return f'$ {capital_cost:,.0f}'
    add_option_row('Retrofit Cost after Incentives', net_capital)

    # -- Simple Payback
    def simple_payback(i):
      payback = options[i]['financial']['simple_payback']
      if payback is not None:
        return f'{payback:.1f} years'
      else:
        return 'None'
    add_option_row('Simple Payback', simple_payback)

    # -- Rate of Return
    def irr(i):
      irr = options[i]['financial']['irr']
      if irr is not None:
        return f'{irr * 100.0: .1f}% / year'
      else:
        return "NA"
    add_option_row('Tax-Free Rate of Return', irr)

    # -- NPV
    def npv(i):
      npv = options[i]['financial']['npv']
      return f'$ {npv:,.0f}'
    add_option_row('Net Present Value (>0 is good)', npv)

    data['tbl_options'] = tbl_options

    # -------------- Render the template
    template_text = app_tables.settings.search(key="analyze-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(**data)

  else:
    # Display input error messages
    template_text = app_tables.settings.search(key="error-report-template")[0]["value"]
    template = env.from_string(template_text)
    return template.render(messages=analyze_results['messages'])
