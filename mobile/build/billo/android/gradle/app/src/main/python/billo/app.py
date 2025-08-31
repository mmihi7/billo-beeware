# src/billo/app.py
import toga
import logging
import asyncio
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from billo.services.auth import get_auth_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BilloApp')

class Billo(toga.App):
    def __init__(self, *args, **kwargs):
        # Initialize the app first
        super().__init__(*args, **kwargs)
        
        # Initialize auth service
        self.auth_service = get_auth_service()
        
        # Initialize screens
        self.welcome_screen = None
        self.terms_screen = None
        self.signin_screen = None
        self.signup_screen = None
        self.home_screen = None
        self.restaurant_dashboard = None
        self._main_window = None

    def startup(self):
        """Construct and show the Toga application."""
        # Create the main window in startup when the Android context is ready
        title = getattr(self, 'formal_name', 'Billo')
        self._main_window = toga.MainWindow(title=title, size=(400, 800))
        
        # Initialize screens
        self._initialize_screens()
        
        # Check if user is already authenticated
        if self.auth_service.is_authenticated():
            self.show_home_screen()
        else:
            self.show_welcome_screen()
        
        # Show the main window
        self._main_window.show()
        
    def _initialize_screens(self):
        """Initialize all screens for the application."""
        try:
            # Import screens
            from .screens.onboarding.welcome import create_welcome_screen
            from .screens.onboarding.terms import create_terms_screen
            from .screens.auth.signin import create_signin_screen
            from .screens.auth.signup import create_signup_screen
            from .screens.home import create_home_screen
            
            # Initialize screens with app instance
            self.welcome_screen = create_welcome_screen(self)
            self.terms_screen = create_terms_screen(self)
            self.signin_screen = create_signin_screen(self)
            self.signup_screen = create_signup_screen(self)
            self.home_screen = create_home_screen(self)
            
        except Exception as e:
            logger.error(f"Failed to initialize screens: {str(e)}")
            self.show_error_screen("Failed to initialize application")
            # Onboarding screens
            from .screens.onboarding.welcome import create_welcome_screen
            from .screens.onboarding.terms import create_terms_screen
            from .screens.auth.signin import create_signin_screen
            from .screens.auth.signup import create_signup_screen
            from .screens.home import create_home_screen
            
            self.welcome_screen = create_welcome_screen(self)
            self.terms_screen = create_terms_screen(self)
            self.signin_screen = create_signin_screen(self)
            self.signup_screen = create_signup_screen(self)
            self.home_screen = create_home_screen(self)
            
        except ImportError as e:
            logger.exception("Failed to load screens:")
            self.show_error_screen(f"Failed to load screens: {e}")
            
    @property
    def main_window(self):
        if self._main_window is None:
            raise RuntimeError("Main window not initialized. Call startup() first.")
        return self._main_window
        
    @main_window.setter
    def main_window(self, window):
        self._main_window = window

    async def handle_signin(self, email, password):
        """Handle the sign-in process."""
        try:
            if not email or not password:
                self.show_error("Error", "Please enter both email and password")
                return
                
            # Show loading indicator
            self.main_window.info_dialog("Signing In", "Please wait...")
            
            # Call auth service
            user = await self.auth_service.sign_in(email, password)
            
            if user:
                # Successful login
                self.show_home_screen()
            else:
                self.show_error("Error", "Invalid email or password")
        except Exception as e:
            logger.error(f"Error during sign in: {str(e)}", exc_info=True)
            self.show_error("Error", "An error occurred during sign in. Please try again.")
    
    async def handle_signup(self, name, email, password, confirm_password):
        """Handle the sign-up process."""
        try:
            # Validate inputs
            if not all([name, email, password, confirm_password]):
                self.show_error("Error", "All fields are required")
                return
                
            if password != confirm_password:
                self.show_error("Error", "Passwords do not match")
                return
                
            # Show loading indicator
            self.main_window.info_dialog("Creating Account", "Please wait...")
            
            # Call auth service
            user = await self.auth_service.sign_up(email, password, {"full_name": name})
            
            if user:
                # Successful signup, show home screen
                self.show_home_screen()
            else:
                self.show_error("Error", "Failed to create account. Please try again.")
        except Exception as e:
            logger.error(f"Error during sign up: {str(e)}", exc_info=True)
            self.show_error("Error", "An error occurred during sign up. Please try again.")
    
    async def handle_logout(self):
        """Handle the logout process."""
        try:
            await self.auth_service.sign_out()
            self.show_welcome_screen()
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}", exc_info=True)
            self.show_error("Error", "Failed to log out. Please try again.")
    
    def show_restaurant_dashboard(self, restaurant_id: str):
        """Show the restaurant dashboard for the given restaurant ID."""
        try:
            from .screens.restaurant.dashboard import create_restaurant_dashboard
            
            # Create a new dashboard instance for this restaurant
            dashboard = create_restaurant_dashboard(self)
            
            # Update the window content
            if self._main_window:
                self._main_window.content = dashboard
            else:
                logger.error("Main window not initialized")
        except ImportError as e:
            logger.exception("Failed to load restaurant dashboard:")
            self.show_error("Error", "Failed to load restaurant dashboard. Please try again.")
        except Exception as e:
            logger.exception("Error showing restaurant dashboard:")
            self.show_error("Error", f"An error occurred: {str(e)}")
    
    def show_home_screen(self):
        """Show the home screen after successful login."""
        if not self._main_window:
            logger.error("Main window not initialized")
            return
            
        if not self.home_screen:
            from .screens.home import create_home_screen
            self.home_screen = create_home_screen(self)
            
        self._main_window.content = self.home_screen
            
    def show_welcome_screen(self):
        """Show the welcome screen."""
        if not self._main_window:
            logger.error("Main window not initialized")
            return
            
        if not self.welcome_screen:
            from .screens.onboarding.welcome import create_welcome_screen
            self.welcome_screen = create_welcome_screen(self)
            
        self._main_window.content = self.welcome_screen
            
    def show_terms_screen(self):
        """Show the terms and conditions screen."""
        if not self._main_window:
            logger.error("Main window not initialized")
            return
            
        if not self.terms_screen:
            from .screens.onboarding.terms import create_terms_screen
            self.terms_screen = create_terms_screen(self)
            
        self._main_window.content = self.terms_screen
            
    def show_signin_screen(self):
        """Show the sign-in screen."""
        if not self._main_window:
            logger.error("Main window not initialized")
            return
            
        if not self.signin_screen:
            from .screens.auth.signin import create_signin_screen
            self.signin_screen = create_signin_screen(self)
            
        self._main_window.content = self.signin_screen
            
    def show_signup_screen(self):
        """Show the sign-up screen."""
        if not self._main_window:
            logger.error("Main window not initialized")
            return
            
        if not self.signup_screen:
            from .screens.auth.signup import create_signup_screen
            self.signup_screen = create_signup_screen(self)
            
        self._main_window.content = self.signup_screen
            
    def show_error_screen(self, message):
        """Show an error screen with the given message."""
        if not self._main_window:
            logger.error("Main window not initialized")
            return
            
        error_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment=CENTER))
        error_label = toga.Label(
            message,
            style=Pack(padding=10, text_align=CENTER, color='red')
        )
        retry_button = toga.Button(
            "Retry",
            on_press=lambda widget: self.startup(),
            style=Pack(padding=10, width=200)
        )
        error_box.add(error_label)
        error_box.add(retry_button)
        self._main_window.content = error_box

def main():
    """The entry point for the application."""
    return Billo('Billo', 'com.billo.mobile')
