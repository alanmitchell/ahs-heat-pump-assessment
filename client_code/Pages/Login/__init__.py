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

    #popup = NameInputPopup()
    #anvil.alert(content=popup, title="Enter your name", large=False, buttons=[])
    #user_name = popup.result
    #print(user_name)
    
    user_id = State.current_user.get_id()
    if State.current_user['is_staff']:
      # staff members work on the last client they worked on from prior session
      State.target_user_id = State.current_user['last_client_id']
    else:
      # clients only get to work on themselves.
      State.target_user_id = user_id
    
    # run server processing that is needed at log in.
    anvil.server.call('user_processing_at_login', user_id)

    # if the name field is empty, show a text box to request it
    # and stay on this form. Open an appropriate form.
    full_name = State.current_user['full_name']
    if full_name is None or len(full_name)==0:
      self.text_box_name.visible = True
    else:
      if State.current_user['is_staff']:
        if State.target_user_id:
          # there already is a target client to go to the Model Inputs page
          open_form('Pages.ModelInputs')
        else:
          # No target client yet, so go select one.
          open_form('Pages.SelectClient')
      else:
        open_form('Pages.HomeInfo')

  def text_box_name_change(self, **event_args):
    """This method is called when the text in this component is edited."""
    pass
