from ._anvil_designer import LoginTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
from ... import State

class Login(LoginTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.layout.panel_staff.visible = False

  def but_login_click(self, **event_args):
    # update State information for the User that just logged in
    State.current_user = anvil.users.login_with_form()
    user_id = State.current_user.get_id()
    State.target_user_id = user_id
    
    # run server processing that is needed at log in.
    anvil.server.call('user_processing_at_login', user_id)
    if State.current_user['is_staff']:
      open_form('Pages.SelectClient')
    else:
      open_form('Pages.HomeInfo')
