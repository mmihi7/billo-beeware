# src/billo/app.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, PADDED

# Import screen creation functions
# Make sure these paths match your actual file structure
from .screens.onboarding.welcome import create_welcome_screen
from .screens.onboarding.terms import create_terms_screen
from .screens.home.home import create_home_screen

class Billo(toga.App):
    def startup(self):
        """Construct and show the Toga application."""
        print("Starting Billo app...")  # Debug print
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        # Set a default size (optional, good for dev mode)
        self.main_window.size = (400, 600)

        print("Creating screens...")  # Debug print
        # Initialize screens by calling the functions from your screen modules
        # Pass 'self' so the screens can call methods like show_terms_screen
        self.welcome_screen = create_welcome_screen(self)
        self.terms_screen = create_terms_screen(self)
        self.home_screen = create_home_screen(self)

        print("Setting initial screen...")  # Debug print
        # Show the initial screen (Welcome)
        self.show_welcome_screen()

        # Show the main window
        print("Showing main window...") # Debug print
        self.main_window.show()
        print("Startup complete")  # Debug print

    def show_welcome_screen(self):
        """Display the welcome screen."""
        print("Showing Welcome Screen") # Debug print
        # Set the content of the main window to the welcome screen's box
        self.main_window.content = self.welcome_screen

    def show_terms_screen(self):
        """Display the terms/permissions screen."""
        print("Showing Terms Screen") # Debug print
        self.main_window.content = self.terms_screen

    def show_home_screen(self):
        """Display the home screen."""
        print("Showing Home Screen") # Debug print
        self.main_window.content = self.home_screen

def main():
    # This is the standard way BeeWare apps are instantiated.
    # The name and package are usually derived from pyproject.toml or command line args,
    # but can be specified directly if needed.
    return Billo()
    # If the above doesn't work due to how briefcase configured the app name/bundle,
    # you might need:
    # return Billo(formal_name="Billo Mobile", app_id="com.billo.mobile")
    # But try the simple `return Billo()` first.
