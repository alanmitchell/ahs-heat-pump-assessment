from ._anvil_designer import DiscussionTemplate
from anvil import *
import anvil.server
from anvil.users import get_user
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Utility import chg_none

class Discussion(DiscussionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.discussion_link.selected = True

    # get the client we are currently working on
    client_id = get_user()["last_client_id"]
    if client_id:
      self.client = anvil.server.call('get_client', client_id)
      self.text_area_discussion.text = chg_none(self.client['discussion'], '')
    else:
      self.client = None

  def text_area_discussion_lost_focus(self, **event_args):
    """Discussion text changed."""
    if self.client:
      discussion = self.text_area_discussion.text
      anvil.server.call('update_client', self.client['row_id'], {'discussion': discussion})
