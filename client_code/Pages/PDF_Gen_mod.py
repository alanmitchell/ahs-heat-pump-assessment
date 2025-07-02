import anvil.server
import os
from fpdf import FPDF
from fpdf import Align
from fpdf.fonts import FontFace
from pypdf import PdfWriter
from anvil.Media import BlobMedia
import anvil.media


### In class PDF, need to put filepath for AHS logo###
### At the very bottom need to put file path for export###
### You will recive a depreciation notice if you don't import the font but it will still work###

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


@anvil.server.callable
def AkHeatSmartPDF(client_name, client_address, ahs_id, assessor,
                   date, square_footage, year_built, heating_system, 
                   current_annual_heating_cost, domestic_hot_water, 
                   electrical_service, *args):
  class PDF(FPDF):
    def header(self):

      self.set_y(19)
      # font
      self.set_font('arial', 'B', 12)
      # Logo
      self.image(name = 'AlaskaHeatSmart.jpg', w=76, keep_aspect_ratio=True, x = Align.C)
      self.ln(2)
      # Calculate width of title and position
      title_w = self.get_string_width(title) + 6
      doc_w = self.w
      self.set_x((doc_w - title_w) / 2)
      # Thickness of frame (border)
      self.set_line_width(1)
      # Title
      self.cell(title_w, 5, title, align='C',)
      # add line
      self.ln(7)
      self.cell(0,h=1, text= '_'*68, align='C')
      # Line break
      self.ln(5)

      # Page footer
    def footer(self):
      # Set position of the footer
      self.set_y(-15)
      # set font
      self.set_font('arial', 'B', 10)
      # Page number
      self.cell(0, 10,
                'Alaska Heat Smart | 9360 Glacier Highway, #202 | Juneau, Alaska 99802 | www.akheatsmart.org',
                align='C')
      # add line
      self.set_y(-20)
      self.cell(0,9, '_'*85, align='C')

      
  def additional_resorces_text( yellow_text):
    '''Changes the text color and size to match AHS's PDF'''
    pdf.ln(10)
    pdf.set_font('arial', 'B', 12)
    pdf.set_text_color(250,140,0)
    pdf.multi_cell(w=0,text=yellow_text)
    pdf.ln(1)
    pdf.set_font(style='',size=11)
    pdf.set_text_color(0,0,0)

  def color_link(h,link_words, link, period = False, cell=False):
    '''Makes links standard blue color with underline and reverts back to normal text'''
    pdf.set_text_color(51,102,204)
    pdf.set_font(style="BU")
    if cell:
      pdf.cell(text=link_words,link = link)
      pdf.set_text_color(0,0,0)
      pdf.set_font(style='')
      if period:
        pdf.cell(text='.')
    else:
      pdf.write(h,link_words,link)
      pdf.set_text_color(0,0,0)
      pdf.set_font(style='')

      if period:
        pdf.write(h,'.')

  def bold_words(h,bold_words):
    '''Makes individual phrases bold and reverts to normal text'''
    pdf.set_font(style="B")
    pdf.write(h,bold_words)
    pdf.set_font(style='')

  title = 'Alaska Heat Smart Home Energy Assessment Report'

  #just filler data currently, I don't think it will be too difficult to make dynamic

  general_table_data = (
    ("Name",f'   {client_name}'),
    ('Address', f'   {client_address}'),
    ('AHS ID', f'   {ahs_id}'),
    ('Assessor', f'   {assessor}'),
    ('Date', f"   {date}")
  )
  home_description_table = (
    ('Square Footage', f'   {square_footage} ft²'),
    ('Year Built', f'   {year_built}'),
    ('Heating System', f'   {heating_system}'),
    ("Current Annual Heating Cost", f"   ${current_annual_heating_cost}"),
    ('Domestic Hot Water', f'   {domestic_hot_water}'),
    ('Electrical Service', f'   {electrical_service}')
  )
  heat_pump_options_table = [
    ['Option'],
    ['Heat Pump Instilation Cost'],
    ["Tax Credits & Incentives"],
    ['Total Net Heat Pump Cost'],
    ['Total Net Cost'],
    ['Annual Electricity Cost Change',],
    ['Net Annual Savings'],
    ['% Reduction Space & HW Cost'],
    ['Payback'],
    ['Remaining Oil Usage'],
    ['Avoided CO2 Emissions']
  ]

  # combines however many options there are (args) into nested list
  for arg in args:
    index = 0
    for elem in arg:
      heat_pump_options_table[index].append(str(elem))
      index += 1

  
  pdf = FPDF

  # Create a PDF object
  pdf = PDF('P', 'mm', 'Letter')

  # Import font (not neccecerry in this version, but without it you get depreciation notices)
  # pdf.add_font("arial", style="", fname="/Users/nikojtgessner/Desktop/HelloWorld/AHS_proj/Automate_pdf_proj/Arial_font/Arial.ttf")
  # pdf.add_font("arial", style="b", fname="/Users/nikojtgessner/Desktop/HelloWorld/AHS_proj/Automate_pdf_proj/Arial_font/Arial_Bold.ttf")
  # pdf.add_font("arial", style="i", fname="/Users/nikojtgessner/Desktop/HelloWorld/AHS_proj/Automate_pdf_proj/Arial_font/Arial_Italic.ttf")
  # pdf.add_font("arial", style="bi", fname="/Users/nikojtgessner/Desktop/HelloWorld/AHS_proj/Automate_pdf_proj/Arial_font/Arial_Bold_Italic.ttf")

  # get total page numbers
  pdf.alias_nb_pages()

  # Set auto page break
  pdf.set_auto_page_break(auto = True, margin = 15)
  pdf.set_margin(25)

  ###PAGE 1#####
  # Add Page
  pdf.add_page()
  # Add donation text
  pdf.multi_cell(w = 0, 
                 text = "NOTE: Alaska Heat Smart Home Energy Assessments cost an average of $175 to cover assessors' time, administrative costs, report writing, and potential follow up. Please help us cover our costs during these challenging financial times by",
                 h = 6, align = 'C')
  pdf.ln(1)
  pdf.cell(w=80,text='making a',align='r')
  color_link(1,'donation.','https://akheatsmart.org/donate/',cell=True)
  # Spacing cell
  pdf.ln(10)


  # Set table font
  pdf.set_font("arial", 'B', size=10)
  # Add general info table
  l=1
  with pdf.table(line_height=10, col_widths = (20,120), text_align = ('LEFT','LEFT')) as table:
    for data_row in general_table_data:
      row = table.row()
      for datum in data_row:
        if l%2 == 1: # this makes left column bold and right column not
          pdf.set_font(style='b')
        else:
          pdf.set_font(style='')
        row.cell(datum)
        l+=1


    # Add home descrition cell
  pdf.set_font('arial', 'B', 11)
  pdf.cell(0,12,'HOME DESCRIPTION')
  # Add honme descrition table
  pdf.set_font('arial', 'B', 10)
  pdf.ln(12)

  # add home description table
  l=1
  with pdf.table(line_height=10, col_widths = (50,100), text_align = ('LEFT','LEFT')) as table:
    for data_row in home_description_table:
      row = table.row()
      for datum in data_row:
        if l%2 == 1:
          pdf.set_font(style='b')
        else:
          pdf.set_font(style='')
        row.cell(datum)
        l+=1







        ### PAGE 2 and 3 ###



  pdf.add_page()
  pdf.set_font(style='b')
  pdf.cell(0,12,'HEAT PUMP OPTIONS')
  pdf.ln(12)
  pdf.set_font(style='')
  pdf.write(5,text= 'OPTION 1: Air Source Heat Pump')
  pdf.ln(10)
  pdf.set_font(style='b')
  pdf.write(5,text= 'Estimated Costs and Savings of Options')
  pdf.ln(5)
  pdf.set_font(style='')
  # add heat pump options table
  ### need to edit incase of more than one option###
  l=1
  with pdf.table(line_height=8,) as table:
    for data_row in heat_pump_options_table:
      row = table.row()
      for tuple in heat_pump_options_table:
        length = len(tuple)
      for datum in data_row:
        if l%length == 1:
          if datum == "Net Annual Savings" or "Total Net Cost":
            pdf.set_font(style='b')
          else:
            pdf.set_font(style="b")
          row.cell(datum, style=FontFace(fill_color=200))
        else:
          pdf.set_font(style='')
          row.cell(datum)           
        l+=1
  pdf.ln(3)


  # loop to print all the explanations
  l=1
  for explen in explanations:
    if l%2 == 1:
      pdf.set_font('arial', '', 12)
      pdf.ln(3)
    else:
      pdf.set_font('arial', 'I', 9)
      pdf.ln(1)
    pdf.multi_cell(w = 0, text=explen)
    # pdf.ln(1)
    l = l+1
  pdf.ln(10)

  pdf.set_font('arial', "B",11)
  pdf.cell(text = "DISCUSSION AND RECOMENDATIONS")
  pdf.ln(7)

  pdf.set_font(style='')
  # pdf.cell(text = 'discussion of heat pump options. ')
  pdf.write(text="Whatever the reviewer wants to write here. The prompt that was previously here will be on the Anvil website instead. If more than the avalible space is used, it will go onto the next page, but the 'Additional Resources' page will always be on it's own.")




  ### Page 4 ### ### Will probably make own pdf





  ### PAGE 5 ###




  pdf.add_page()
  pdf.set_font(style='B', size= 15)
  pdf.ln(10)
  pdf.cell(w=0, text='HEAT PUMP LOAN ELIGIBILITY AUTHORIZATION', align='C')
  pdf.set_font(style='', size=12)
  pdf.ln(10)
  pdf.multi_cell(w = 0, text = 'Alaska Heat Smart authorizes that the holder of this Heat Pump Home Assessment report meets the report receipt eligibility requirement for a Heat Pump Loan, under the terms of the Alaska Heat Smart Heat Pump Purchase Loan agreement with True North Federal Credit Union or Tongass Federal Credit Union.', h = 6, align = 'C')
  pdf.ln(4)
  pdf.cell(0,h=1, text= '_'*68, align='C')
  between_spacing = 12
  pdf.ln(30)
  pdf.set_font(style="b")
  pdf.write(5, f'Homeowner:   {client_name}')
  pdf.ln(between_spacing)
  pdf.write(5, f'Address:   {client_address}')
  pdf.ln(between_spacing)
  pdf.write(5, f'AHS Energy Advisor:   {ahs_energy_advisor}')
  pdf.ln(between_spacing)
  pdf.write(5, f'Date:   {date}')


  byte_string = pdf.output(dest='S').encode('latin-1')

  # Create an Anvil Media object from the encoded bytes.
  pdf= BlobMedia("application/pdf", byte_string, name="new_file.pdf")
  retun pdf






AkHeatSmartPDF(client_name, client_address, ahs_id, assessor, date, 
               square_footage, year_built, heating_system, current_annual_heating_cost,
               domestic_hot_water, electrical_service, heat_pump_1,heat_pump_2)

