# src/billo/screens/home/home.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, PADDED

def create_home_screen(app_instance):
    home_box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))

    title_label = toga.Label(
        "Billo Home",
        style=Pack(padding=(10, 10), font_size=18, text_align=CENTER)
    )

    # Card 1: Connect to Restaurant
    connect_button = toga.Button(
        "Connect to a Restaurant",
        on_press=lambda widget: print("Connect button pressed"), # Placeholder action
        style=Pack(padding=5, height=60) # Style the button like a card if possible
    )

    # Card 2: Saved Restaurants (Initially inactive/disabled)
    saved_button = toga.Button(
        "Saved Restaurants (0)", # Placeholder count
        enabled=False, # Initially inactive
        on_press=lambda widget: print("Saved Restaurants button pressed"), # Placeholder action
        style=Pack(padding=5, height=60)
    )

    # Add widgets
    home_box.add(title_label)
    home_box.add(connect_button)
    home_box.add(saved_button)

    # Potentially add logic here or in app.py to enable saved_button
    # when restaurants are actually saved.

    return home_box
