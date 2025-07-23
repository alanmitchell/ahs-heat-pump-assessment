import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

import zipfile 
from io import BytesIO
from anvil import BlobMedia

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


@anvil.server.callable
def save_user_image(floorplan):
  """Save the uploaded image to the current user's row in the users table"""

  current_user = anvil.users.get_user()
  if current_user is None:
    return {"success": False, "message": "User not logged in"}

  try:
    # Find the user's row in your data table
    current_user['Floorplan'] = floorplan
    return {"success": True, "message": "Image uploaded successfully"}
  except Exception as e:
    return {"success": False, "message": f"Error saving floorplan image: {str(e)}"}

@anvil.server.callable
def save_additional_images(image_list: list):
    """Save multiple images as a ZIP file in a single table cell"""

    current_user = anvil.users.get_user()
    if current_user is None:
      return {"success": False, "message": "User not logged in"}

    try:
      # Create ZIP file in memory
      zip_buffer = BytesIO()

      with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, image_media in enumerate(image_list):
          # Get the image data
          image_data = image_media.get_bytes()

          # Determine file extension from content type or use a default
          content_type = getattr(image_media, 'content_type', 'image/jpeg')
          if 'png' in content_type.lower():
            ext = 'png'
          elif 'gif' in content_type.lower():
            ext = 'gif'
          else:
            ext = 'jpg'

            # Add to ZIP with a sequential filename
          filename = f"image_{i+1}.{ext}"
          zip_file.writestr(filename, image_data)

        # Create Media object from ZIP
      zip_media = BlobMedia(
        content_type="application/zip",
        content=zip_buffer.getvalue(),
        name="user_images.zip"
      )

      # Save to database
      
      current_user['Additional Images'] = zip_media

      return {"success": True, "message": f"Successfully saved {len(image_list)} images"}

    except Exception as e:
      return {"success": False, "message": f"Error: {str(e)}"}


  
  # current_user = anvil.users.get_user()
  # if current_user is None:
  #   return {"success": False, "message": "User not logged in"}
  # try:
  #   if current_user['Additional Images'] is None:
  #     buffer =  BytesIO()
  #     with ZipFile(buffer,'w') as zip:
  #       for image in additional_images:
  #        zip_file = zip.write(image)
  #     buffer.close()
  # except Exception as e:
  #   return{"success": False, "message": f"Error saving additional images: {str(e)}"}