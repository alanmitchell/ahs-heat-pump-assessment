from ._anvil_designer import FullImageFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class FullImageForm(FullImageFormTemplate):
    def __init__(self, img_media, **properties):
      self.init_components(**properties)
      self.image_full.source = img_media

