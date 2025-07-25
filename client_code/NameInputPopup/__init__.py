from ._anvil_designer import NameInputPopupTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class NameInputPopup(NameInputPopupTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.card_content_container_1.width = "300px"

  def button_ok_click(self, **event_args):
    """This method is called when the component is clicked."""
    self.raise_event('x-close', value=self.text_box_name.text)
