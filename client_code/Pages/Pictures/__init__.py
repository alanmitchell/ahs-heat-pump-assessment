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
    self.files_list.add_event_handler('x-delete-file-item', self.handle_delete_item)
    self.floorplan_files.add_event_handler('x-delete-floorplan-item', self.handle_delete_item_floorplan)
    self.image_thumb.set_event_handler('click', self.show_full_image)


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

  def additional_images_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
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

  def read_current_files(self, colunm):
    """Extract images from the ZIP file"""

    current_user = anvil.users.get_user()
    if current_user is None:
      return {"success": False, "images": []}

    try:
      if current_user is None or current_user[colunm] is None:
        return {"success": True, "images": []}

      zip_media = current_user[colunm]
      zip_data = zip_media.get_bytes()

      images = []
      with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_file:
        for filename in zip_file.namelist():
          if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_data = zip_file.read(filename)

          # Determine content type
            if filename.lower().endswith('.png'):
              content_type = 'image/png'
            else:
              content_type = 'image/jpeg'
  
            # Create Media object
            image_media = BlobMedia(
              content_type=content_type,
              content=image_data,
              name=filename
            )
            images.append(image_media)

      return {"success": True, "images": images}

    except Exception as e:
      return {"success": False, "message": f"Error: {str(e)}", "images": []}


      














