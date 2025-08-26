from ._anvil_designer import LoginTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

class Login(LoginTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def but_login_click(self, **event_args):
    cur_user = anvil.users.login_with_form(show_signup_option=False)

    # run server processing that is needed at log in.
    anvil.server.call('user_processing_at_login')

    # if the name field is empty, show a text box to request it
    # and stay on this form. Open an appropriate form.
    full_name = cur_user['full_name']
    if full_name is None or len(full_name)==0:
      self.flow_panel_name.visible = True
    else:
      navigate_to_next_form()

  def button_save_name_click(self, **event_args):
    """This method is called when the component is clicked."""
    anvil.server.call('update_user_info', {'full_name': self.text_box_name.text})
    navigate_to_next_form()

  def button_1_click(self, **event_args):
    """This method is called when the component is clicked."""
    anvil.users.signup_with_email('info@analysisnorth.com', 'test123')

def navigate_to_next_form():
  if anvil.users.get_user()['last_client_id']:
    # there already is a target client to go to the Model Inputs page
    open_form('Pages.ModelInputs')
  else:
    # No target client yet, so go select one.
    open_form('Pages.SelectClient')
