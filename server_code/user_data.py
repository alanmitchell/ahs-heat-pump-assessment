import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_users_public_fields():
  """Returns publicly-viewable User fields."""
  return [
    {'id': u.get_id(), 'email': u['email'], 'is_staff': u['is_staff'], 'full_name': u['full_name']}
    for u in app_tables.users.search()
  ]

@anvil.server.callable
def user_processing_at_login(user_id):
  """Does any server-side processing that is needed after a user logs in."""
  user = app_tables.users.get_by_id(user_id)
  if user:
    # check to see if user has an Alaska Heat Smart email, and if so, make them a 
    # staff user.
    if user['email'].lower().endswith('akheatsmart.org'):
      # only do this one time (field is None initially)
      if user['is_staff'] is None:
        user['is_staff'] = True

    # If the the user is a Client, add records to the ClientData and Options table
    # if they do not exist.
    if not current_user_is_staff():
      result = app_tables.clientdata.search(client=user)
      if len(result)==0:
        app_tables.clientdata.add_row(client=user)
      result = app_tables.options.search(client=user)
      if len(result)==0:
        # add 3 options to the table
        app_tables.options.add_row(client=user, option_number=1)
        app_tables.options.add_row(client=user, option_number=2)
        app_tables.options.add_row(client=user, option_number=3)

@anvil.server.callable
def update_user_info_by_staff(user_id, field_dict):
  """Allows a currently logged-in staff user to update fields of any user row,
  identified by 'user_id'. 'field_dict' has the the field names and values that
  are to be changed."""
  if current_user_is_staff():
    user = app_tables.users.get_by_id(user_id)
    if user:
      for field_name, val in field_dict.items():
        user[field_name] = val

@anvil.server.callable
def update_user_full_name(full_name):
  cur_user = anvil.users.get_user()
  if cur_user:
    cur_user['full_name'] = full_name

def current_user_is_staff():
  """Returns True if current user is a Staff user."""
  cur_user = anvil.users.get_user()
  if cur_user is not None and cur_user['is_staff']:
    return True
  else:
    return False


# @anvil.server.callable
# def add_pictures(floorplan=floorplan,
#                 *additional_pics):
#   cur_user = anvil.users.get_user()
#   row = app_tables.people.get(email=cur_user)
#   row['Floorplan'] = floorplan
#   # row['Additional Pictures']

# def add_pic(floorplan=floorplan, *additional_pics):
#   # Find the user's row in your data table
#   current_user = anvil.users.get_user()
#   user_row = app_tables.users.get(user=current_user)

#   if user_row is None:
#     # Create a new row if the user doesn't exist in the table
#     user_row = app_tables.users.add_row(
#       user=current_user,
#       floorplan=floorplan  # Assuming your Media column is named 'profile_image'
#     )
#   else:
#     # Update the existing row
#     user_row['profile_image'] = uploaded_file


@anvil.server.callable
def save_user_image(uploaded_file):
  """Save the uploaded image to the current user's row in the users table"""

  # Get the current user
  current_user = anvil.users.get_user()

  if current_user is None:
    return {"success": False, "message": "User not logged in"}

  try:
    # Find the user's row in your data table
    user_row = app_tables.users.get()

    if user_row is None:
      # Create a new row if the user doesn't exist in the table
      user_row = app_tables.users.add_row(
        user=current_user,
        floorplan=uploaded_file
      )
      return {"success": True, "message": "New user profile created with image"}
    else:
      # Update the existing row
      user_row['Floorplan'] = uploaded_file
      return {"success": True, "message": "Image uploaded successfully"}

  except Exception as e:
    return {"success": False, "message": f"Error saving image: {str(e)}"}

  
