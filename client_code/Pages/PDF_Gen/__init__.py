from ._anvil_designer import PDF_GenTemplate
from anvil import *
import anvil.users

class PDF_Gen(PDF_GenTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
