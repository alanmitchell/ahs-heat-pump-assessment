from ._anvil_designer import AdminTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Admin(AdminTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.admin_link.selected = True

    self.all_users = anvil.server.call('get_users_public_fields')
    self.repeating_panel_is_staff.items = self.all_users

  def text_search_email_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    query = self.text_search_email.text.strip().lower()
    self.repeating_panel_is_staff.items = [
      u for u in self.all_users
      if query in u['email'].lower()
    ]

