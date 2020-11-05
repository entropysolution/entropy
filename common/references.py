import os
from common.release import fetch_git_release

GENERIC_ERROR_MESSAGE = "The application has encountered an unknown error."
RELEASE = fetch_git_release()
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')