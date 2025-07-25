from ._anvil_designer import ItemTemplate3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .FullImageForm import FullImageForm

class ItemTemplate3(ItemTemplate3Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.file_image.source=self.item
    self.file_name.text = self.item.name
    self.file_image.set_event_handler('x-click', self.show_full_image)

  def delete_button_click(self, **event_args):
    self.parent.raise_event('x-delete-floorplan-item', item_to_delete=self.item)

  def file_caption_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    pass

  def show_full_image(self, **event_args):
    # Show the full image in a lightbox/dialog
    full_form = FullImageForm(self._original_media)
    anvil.alert(full_form, title="Full-Size Photo")