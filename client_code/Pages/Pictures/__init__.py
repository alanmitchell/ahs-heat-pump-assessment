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
    """This method is called when the submit botton is clicked."""
    anvil.server.call('add_pictures', floorplan)
  def floorplan_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    file=floorplan
    

def file_uploaded(uploader, destination):
  