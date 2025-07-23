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
    self.image_names = ''

  def submit_click(self, **event_args):
    # Get the uploaded file from the FileLoader
    uploaded_file = self.floorplan.file
    additional_pics = self.additional_pics

    if (uploaded_file is None) and (additional_pics == []):
      alert("Please select an image to upload")
      return

    # Call the server function
    if uploaded_file is not None:
      try:
        result = anvil.server.call('save_user_image', uploaded_file)
        if result['success']:
          alert(result['message'])
          # Optionally clear the file loader
          self.floorplan.clear()
        else:
          alert(f"Floorplan upload failed: {result['message']}")
      except Exception as e:
        alert(f"Error uploading image: {str(e)}")
    
    if additional_pics is not None:
      try:
        result = anvil.server.call('save_additional_images', additional_pics)
        if result['success']:
          alert(result['message'])
        # Optionally clear the file loader
          self.additional_images.clear()
        else:
          alert(f"Floorplan upload failed: {result['message']}")
      except Exception as e:
        alert(f"Error uploading image: {str(e)}")
        
  def floorplan_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    self.floorplan_image.source = file
    self.floorplan = file


  def additional_images_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    self.additional_photos_image.source = file
    self.additional_pics.append(file)
    self.image_names += f'{file.name}\n'
    self.additional_images_files_show()


  def additional_images_files_show(self, **event_args):
    """This method is called when the component is shown on the screen."""
    self.additional_images_files.text = self.image_names




