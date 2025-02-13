import os
import sys

# Add the app directory to the Python path
project_home = '/home/gerfz/casino-banner-system'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import and create the Flask app
from app import app as application

# Set the working directory
os.chdir(project_home)
