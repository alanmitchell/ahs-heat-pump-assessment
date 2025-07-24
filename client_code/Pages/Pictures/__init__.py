from ._anvil_designer import PicturesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Pictures(PicturesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.pictures_link.selected = True
    self.additional_pics = []
    self.floorplan_pics = []
    self.image_names = ''
    self.files_list.add_event_handler('x-delete-file-item', self.handle_delete_item)
    self.floorplan_files.add_event_handler('x-delete-floorplan-item', self.handle_delete_item_floorplan)

  def submit_click(self, **event_args):
    # Get the uploaded file from the FileLoader
    floorplan_pics = self.floorplan_pics
    additional_pics = self.additional_pics

    if (floorplan_pics is None) and (additional_pics == []):
      alert("Please select an image to upload")
      return

    # Call the server function
    if len(floorplan_pics) !=0:
      try:
        result = anvil.server.call('save_multiple_images', floorplan_pics, 'Floorplan')
        if result['success']:
          alert(result['message'])
          # Optionally clear the file loader
          self.floorplan.clear()
        else:
          alert(f"Floorplan upload failed: {result['message']}")
      except Exception as e:
        alert(f"Error uploading floorplan image(s): {str(e)}")
    
    if len(additional_pics) !=0:
      try:
        result = anvil.server.call('save_multiple_images', additional_pics,'Additional Images')
        if result['success']:
          alert(result['message'])
        # Optionally clear the file loader
          self.additional_images.clear()
        else:
          alert(f"Additional images upload failed: {result['message']}")
      except Exception as e:
        alert(f"Error uploading additional image(s): {str(e)}")
        
  def floorplan_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    for fl in self.floorplan.files:
      self.floorplan_pics.append(fl)
    self.floorplan_files.items = self.floorplan_pics



  def additional_images_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    # self.additional_photos_image.source = file
    for fl in self.additional_images.files:
      self.additional_pics.append(fl)
    self.files_list.items = self.additional_pics

  def handle_delete_item(self, item_to_delete, **event_args):
    """Handle delete event from repeating panel items"""
    if item_to_delete in self.additional_pics:
      self.additional_pics.remove(item_to_delete)
      self.files_list.items = self.additional_pics
 
  def handle_delete_item_floorplan(self, item_to_delete, **event_args):
    """Handle delete event from repeating panel items"""
    if item_to_delete in self.floorplan_pics:
      self.floorplan_pics.remove(item_to_delete)
      self.floorplan_files.items = self.floorplan_pics

  def button_1_click(self, **event_args):
    """This method is called when the component is clicked."""
    print('button clicked!!!')













