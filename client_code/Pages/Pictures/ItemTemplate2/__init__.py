from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate2(ItemTemplate2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
       # Any code you write here will run before the form opens.
    self.file_image.source=self.item
    self.file_name.text = self.item.name

  def delete_button_click(self, **event_args):
    # self.item.delete()
    self.items.remove(self.item)
    open_form('Pages.Pictures')