from ._anvil_designer import MediaItemsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .FullImageForm import FullImageForm
from .... import State
import time

class MediaItems(MediaItemsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.user_id = State.target_user_id
    self.row_id = self.item['row_id']
    self.file_image.source=self.item['media_object']
    self.file_name.text = self.item['media_object'].name
    if self.item['category']:
      self.file_catagory.selected_value = self.item['category']
    self.file_caption.text = self.item['caption']
  
  def delete_button_click(self, **event_args):
    anvil.server.call('delete_media',self.row_id)
    self.parent.raise_event('x-delete-floorplan-item', item_to_delete=self.item)

  def file_caption_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    start_text = self.file_caption.text
    time.sleep(2)
    if start_text == self.file_caption.text:
      dict = {'row_id':self.row_id, 'caption':self.file_caption.text}
      anvil.server.call('store_media', self.user_id, dict)
      print('executed')

  def file_image_mouse_up(self, x, y, button, **event_args):
    """This method is called when a mouse button is released on this component"""
    full_form = FullImageForm(self.item['media_object'])
    anvil.alert(full_form, title="Full-Size Photo", large=True)

  def file_catagory_change(self, **event_args):
    """This method is called when an item is selected"""
    dict = {'row_id':self.row_id, 'category':self.file_catagory.selected_value}
    self.parent.raise_event('x-change-media-summary')
    anvil.server.call('store_media', self.user_id, dict)

  def file_download_click(self, **event_args):
    """This method is called when the component is clicked."""
    Link(text='Open File', url=self.item)

  def open_file_click(self, **event_args):
    """This method is called clicked"""
    self.open_file.url = self.item['media_object']

 

    
 