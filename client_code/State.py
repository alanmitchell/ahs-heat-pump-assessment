import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

# The currently logged-in User (full object)
current_user = None

# The ID of the User whose data will populate the editing forms.
target_user_id = None