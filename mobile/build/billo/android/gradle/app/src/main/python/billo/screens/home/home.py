# src/billo/screens/home/home.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import json
import asyncio

# For QR code scanning (using opencv-python)
try:
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    HAS_QR_LIBS = True
except ImportError:
    HAS_QR_LIBS = False

def create_home_screen(app_instance):
    home_box = toga.Box(style=Pack(direction=COLUMN, margin=10, flex=1))

    title_label = toga.Label(
        "Billo Home",
        style=Pack(margin=(10, 10), font_size=18, text_align=CENTER)
    )

    # Card 1: Connect to Restaurant with QR Scanner
    async def scan_qr_code(widget):
        if not HAS_QR_LIBS:
            await app_instance.main_window.info_dialog(
                "Dependencies Missing",
                "Please install required packages for QR code scanning.\n\n"
                "Run: pip install opencv-python pyzbar numpy"
            )
            return

        try:
            # In a real app, this would open the device camera
            # For now, we'll simulate a successful scan
            await asyncio.sleep(1)  # Simulate scanning delay
            
            # Simulated QR code data (in real app, this would come from the camera)
            qr_data = json.dumps({
                "restaurant_id": "rest_123",
                "restaurant_name": "Sample Restaurant",
                "table_number": "5"
            })
            
            # Parse the QR code data
            try:
                data = json.loads(qr_data)
                restaurant_id = data.get('restaurant_id')
                restaurant_name = data.get('restaurant_name', 'Unknown Restaurant')
                table_number = data.get('table_number', '1')
                
                # Show connection confirmation
                confirmed = await app_instance.main_window.confirm_dialog(
                    "Connect to Restaurant",
                    f"Connect to {restaurant_name} at Table {table_number}?"
                )
                
                if confirmed:
                    # In a real app, you would connect to the restaurant's system here
                    # For now, we'll just show the restaurant screen
                    app_instance.show_customer_restaurant(
                        tab_number=table_number,
                        restaurant_name=restaurant_name
                    )
                    
            except json.JSONDecodeError:
                await app_instance.main_window.error_dialog(
                    "Invalid QR Code",
                    "The scanned QR code is not a valid Billo restaurant code."
                )
                
        except Exception as e:
            await app_instance.main_window.error_dialog(
                "Scan Failed",
                f"Failed to scan QR code: {str(e)}"
            )

    connect_button = toga.Button(
        "Scan QR Code to Connect to Restaurant",
        on_press=lambda widget: asyncio.create_task(scan_qr_code(widget)),
        style=Pack(margin=5, height=60, padding=10, background_color='#4CAF50', color='white')
    )

    # Card 2: Saved Restaurants (Initially inactive/disabled)
    saved_button = toga.Button(
        "Saved Restaurants (0)", # Placeholder count
        enabled=False, # Initially inactive
        on_press=lambda widget: print("Saved Restaurants button pressed"), # Placeholder action
        style=Pack(margin=5, height=60)
    )

    # Add widgets
    home_box.add(title_label)
    home_box.add(connect_button)
    home_box.add(saved_button)

    # Potentially add logic here or in app.py to enable saved_button
    # when restaurants are actually saved.

    return home_box
