import sys

PROJECT_DIR = '/var/www/idservice'

sys.path.append(PROJECT_DIR)

from app import app as application


