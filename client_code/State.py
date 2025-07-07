import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
# The currently logged-in U1ser
current_user = None

# The User whose data will populate the editing forms.
target_user = None