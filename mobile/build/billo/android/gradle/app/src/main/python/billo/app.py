# src/billo/minimal_app.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

class Billo(toga.App):
    def startup(self):
        """Construct and show the Toga application."""
        # Create the main window (MANDATORY for Android)
        title = getattr(self, 'formal_name', 'Billo')
        self.main_window = toga.MainWindow(title=title, size=(400, 800))
        
        # Create a simple box with a label
        box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        # Add a welcome label
        label = toga.Label(
            "Billo is running!",
            style=Pack(font_size=20, text_align=CENTER, padding_bottom=20)
        )
        box.add(label)
        
        # Add a status label
        status = toga.Label(
            "App initialized successfully!",
            style=Pack(text_align=CENTER, color='green')
        )
        box.add(status)
        
        # Set the content of the main window
        self.main_window.content = box
        
        # Show the main window (MANDATORY for Android)
        self.main_window.show()

def main():
    """The entry point for the application."""
    return Billo('Billo', 'com.billo.mobile')
