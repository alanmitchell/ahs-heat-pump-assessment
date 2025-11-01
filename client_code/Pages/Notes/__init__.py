from ._anvil_designer import NotesTemplate
from anvil import *
import m3.components as m3
import anvil.server
from anvil.users import get_user
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Utility import chg_none, active_client_name

class Notes(NotesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.notes_link.selected = True
    self.set_event_handler('show', self.form_show)

    # get the client we are currently working on
    client_id = get_user()["last_client_id"]
    if client_id:
      self.client = anvil.server.call('get_client', client_id)
      self.text_area_notes.text = chg_none(self.client['assessor_notes'], '')
    else:
      self.client = None
  
  def form_show(self, **event_args):
    self.layout.rich_text_client_name.content = f'**Client:** {active_client_name()}'

  def text_area_notes_lost_focus(self, **event_args):
    """This method is called when the component loses focus."""
    # get the client we are currently working on
    if self.client:
      notes = self.text_area_notes.text
      anvil.server.call('add_update_client', self.client['row_id'], {'assessor_notes': notes})
