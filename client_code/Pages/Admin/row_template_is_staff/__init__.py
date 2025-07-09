from ._anvil_designer import row_template_is_staffTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class row_template_is_staff(row_template_is_staffTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def checkbox_is_staff_change(self, **event_args):
    """This method is called when the component is checked or unchecked"""
    self.item['is_staff'] = self.checkbox_is_staff.checked
    anvil.server.call('update_user_info_by_staff', self.item['id'], {'is_staff': self.checkbox_is_staff.checked})
