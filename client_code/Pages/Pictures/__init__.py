from ._anvil_designer import PicturesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# import zipfile
# import io

class Pictures(PicturesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.pictures_link.selected = True
    self.additional_pics = []
    self.floorplan_pics = []
    self.floorplan_files.add_event_handler('x-delete-floorplan-item', self.handle_delete_item_floorplan)
    


  def submit_click(self, **event_args):
    # Get the uploaded file from the FileLoader
    floorplan_pics = self.floorplan_pics
    additional_pics = self.additional_pics

    if (floorplan_pics == []) and (additional_pics == []):
      alert("Please select an image to upload")
      return

    if len(floorplan_pics) != []:
      try:
        result = anvil.server.call('save_multiple_images', floorplan_pics, 'Floorplan')
        if result['success']:
          alert(result['message'])
          floorplan_pics = [] #clears out files
          self.floorplan_files.items = floorplan_pics
        else:
          alert(f"Floorplan upload failed: {result['message']}")
      except Exception as e:
        alert(f"Error uploading floorplan image(s): {str(e)}")
    
    if len(additional_pics) != []:
      try:
        result = anvil.server.call('save_multiple_images', additional_pics,'Additional Images')
        if result['success']:
          alert(result['message'])
          additional_pics = [] #clears out files
          self.files_list.items = additional_pics
        else:
          alert(f"Additional images upload failed: {result['message']}")
      except Exception as e:
        alert(f"Error uploading additional image(s): {str(e)}")
        
  def floorplan_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    for fl in self.floorplan.files:
      self.floorplan_pics.append(fl)
    self.floorplan_files.items = self.floorplan_pics

 
  def handle_delete_item_floorplan(self, item_to_delete, **event_args):
    """Handle delete event from repeating panel items"""
    if item_to_delete in self.floorplan_pics:
      self.floorplan_pics.remove(item_to_delete)
      self.floorplan_files.items = self.floorplan_pics

  def image_resize(self,image):
    width, height = image.get_dimentions(image)
    if width > 1500:
      new_height = height * (1500/width)
      resized_image  = anvil.media.resize_media(image, width=1500, height=new_height)
      return resized_image
    if height > 1500:
      new_width = width * (1500/height)
      resized_image = anvil.media.resize_media(image, width=new_width, height = 1500)
      return resized_image
    else:
      return image

 

  

      














