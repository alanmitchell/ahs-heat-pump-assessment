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

  def submit_click(self, **event_args):
    # Get the uploaded file from the FileLoader
    uploaded_file = self.floorplan.file

    if uploaded_file is None:
      alert("Please select an image to upload")
      return

    # Call the server function
    try:
      result = anvil.server.call('save_user_image', uploaded_file)

      if result['success']:
        alert(result['message'])
        # Optionally clear the file loader
        self.floorplan.clear()
      else:
        alert(f"Upload failed: {result['message']}")

    except Exception as e:
      alert(f"Error uploading image: {str(e)}")
    
  def floorplan_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    self.floorplan_image.source = file
    self.floorplan = file
    # self.floorplan_imageImage.source = self.image_1.source
    
