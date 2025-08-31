# src/billo/screens/onboarding/welcome.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

def create_welcome_screen(app_instance):
    # Create the main box for the screen
    welcome_box = toga.Box(style=Pack(
        direction=COLUMN,
        padding=20,
        alignment=CENTER,
        flex=1
    ))

    # Add a label for the welcome message
    welcome_label = toga.Label(
        "Welcome to Billo!",
        style=Pack(
            padding=(10, 10),
            font_size=20,
            text_align=CENTER,
            flex=1
        )
    )

    # Add a button to proceed to the next screen (Terms)
    next_button = toga.Button(
        "Get Started",
        on_press=lambda widget: app_instance.show_terms_screen(),
        style=Pack(
            padding=(35, 15, 15, 15),  # Increased top padding to create space
            width=300,
            background_color='#1E88E5',
            color='white',
            font_weight='bold'
        )
    )

    # Add widgets to the box
    welcome_box.add(welcome_label)
    # You might want vertical space; Toga often uses Boxes or padding for layout
    # For simplicity, we add the button directly. You can add spacers if needed.
    welcome_box.add(next_button)

    # Create a Window for this screen (optional if using main window switching)
    # For now, we'll return the box to be placed in the main window
    return welcome_box
