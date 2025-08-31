import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Now import and run the app
from billo.app import main

if __name__ == '__main__':
    app = main()
    app.main_loop()
