from ._anvil_designer import PicturesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import State
import anvil.image



class Pictures(PicturesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.pictures_link.selected = True
    self.user_id = State.target_user_id
    self.media_files = self.get_media()
    
    self.floorplan_files.items = self.media_files
    self.floorplan_files.add_event_handler('x-delete-floorplan-item', self.handle_delete_item_floorplan)
    self.floorplan_files.add_event_handler('x-change-media-summary', self.media_summary_show)
    
        
  def floorplan_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    # self.media_files = self.get_media()
    if anvil.users.get_user() is None:
      alert('Please sign in.')
      return
    for fl in self.floorplan.files:
      print(fl.content_type)
      if 'image' in fl.content_type:
        fl = self.image_resize(fl) # lose all metadata besides name
      dict = {'row_id':None, 'media_object':fl, 'category':'', 'caption':''}
      dict['row_id'] = anvil.server.call('store_media', self.user_id, dict)
      print('uploaded')
      self.media_files.insert(0,dict)
    self.media_summary_show()
    self.floorplan_files.items = self.media_files

  def get_media(self):
    initial_media_files = anvil.server.call('get_all_media_for_user', self.user_id)
    newlist = sorted(initial_media_files, key=lambda d: d['date_time_added'], reverse=True)
    return newlist
  
  def handle_delete_item_floorplan(self, item_to_delete, **event_args):
    """Handle delete event from repeating panel items"""
    # self.media_files = self.get_media()
    self.media_summary_show()
    self.floorplan_files.items = self.media_files

  def image_resize(self,file):
    image = anvil.image.generate_thumbnail(file,1500)
  # image = anvil.image.generate_thumbnail(image_media,1500)
    image_bytes = image.get_bytes()
    return BlobMedia(
    content_type=file.content_type,
    content=image_bytes, 
    name=file.name)

  def media_summary_show(self, **event_args):
    """This method is called when the component is shown on the screen."""
    self.media_files = self.get_media()
    cat_counts = {}
    text = 'Media Summary:\n'
    for media in self.media_files:
      if media['category'] in cat_counts.keys():
        cat_counts[media['category']] += 1
      else:
        cat_counts[media['category']] = 1
    for key, value in cat_counts.items():
      if key == '':
        key = 'Unassigned'
      text += f'{key}: {value}\n'
    self.media_summary.text = text

  def heading_1_show(self, **event_args):
    """This method is called when the component is shown on the screen."""
    pass

  def search_box_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    query = self.search_box.text.strip().lower()
    self.floorplan_files.items = [
      u for u in self.media_files
      if query in u['media_object'].name.lower()]
    self.floorplan_files.
    

 





