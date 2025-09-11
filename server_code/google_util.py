"""Module to interact with Google files and documents.
"""
import time, json

from anvil.users import get_user
from anvil import app_tables
import anvil.secrets

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def _drive():
  """Build Drive client from secret (no filesystem writes needed)
  """
  sa_info = json.loads(anvil.secrets.get_secret('GOOGLE_SA_JSON'))
  creds = service_account.Credentials.from_service_account_info(
    sa_info, scopes=['https://www.googleapis.com/auth/drive']
  )
  return build('drive', 'v3', credentials=creds)

def _retry(func, *args, **kwargs):
  """Retry 429/5xx with simple exponential backoff
  """
  for attempt in range(5):
    try:
      return func(*args, **kwargs)
    except HttpError as e:
      status = getattr(getattr(e, 'resp', None), 'status', None)
      if status in (429, 500, 502, 503, 504):
        time.sleep(2 ** attempt)  # 1,2,4,8,16s
        continue
      raise

def copy_template_into_folder(template_file_id: str,     # Google ID of template file
                              target_folder_id: str,     # Google ID of target folder
                              new_name: str) -> str:     # New name of copied file
  """Copies a template file into a target folder and gives the new file a name.
  Returns the Google ID of the newly created file.
  """
  drv = _drive()
  # Copy into target folder
  copy_req = drv.files().copy(
    fileId=template_file_id,
    supportsAllDrives=True,
    body={'name': new_name, 'parents': [target_folder_id]}
  )
  new_file = _retry(copy_req.execute)
  return new_file['id']

@anvil.server.callable
def make_client_historical_use_ss(ss_name: str) -> str:
  """Creates a new Historical Use Google Sheet for a client and returns the Google
  file ID of that Sheet. Uses a template file to create the sheet.
  """
  if get_user():
    # only logged-in users can access.
    template_id = app_tables.settings.search(key="historical-use-file-id")[0]["value"]
    folder_id = app_tables.settings.search(key="client-document-folder-id")[0]["value"]
    new_file_id = copy_template_into_folder(template_id, folder_id, ss_name)
    return new_file_id

  else:
    return None