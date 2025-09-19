from ._anvil_designer import row_template_select_clientTemplate
from anvil import *
import m3.components as m3
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class row_template_select_client(row_template_select_clientTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def button_select_click(self, **event_args):
    # need to raise this event on the parent of this form to have Main form
    # receive it.
    self.parent.raise_event("x-row-selected", item=self.item)
