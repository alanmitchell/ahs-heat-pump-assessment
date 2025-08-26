from ._anvil_designer import SignupDialogTemplate
from anvil import *
import anvil.server

class SignupDialog(SignupDialogTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.email_box.placeholder = "you@akheatsmart.org"
    self.pw_box.hide_text = True
    self.pw2_box.hide_text = True
    self.signup_btn.role = "default"

  def cancel_btn_click(self, **event_args):
    # Close the alert without creating an account
    self.raise_event('x-close-alert', value={"status":"cancel"})
  
  def signup_btn_click(self, **event_args):
    email = (self.email_box.text or "").strip()
    pw    = self.pw_box.text or ""
    pw2   = self.pw2_box.text or ""

    # Light client-side checks (authoritative checks happen on the server)
    if not email or "@" not in email:
      Notification("Please enter a valid email address.", style="warning").show()
      return
    if pw != pw2:
      Notification("Passwords do not match.", style="warning").show()
      return
    if len(pw) < 8:
      Notification("Use at least 8 characters for your password.", style="warning").show()
      return

    try:
      anvil.server.call('restricted_signup', email, pw)
      # Don’t auto-login because confirmation is required
      self.raise_event('x-close-alert', value={"status":"success"})
    except Exception as e:
      Notification(str(e), style="danger").show()
