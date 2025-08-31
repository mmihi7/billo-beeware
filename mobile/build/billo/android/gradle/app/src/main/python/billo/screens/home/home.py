# src/billo/screens/home/home.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import json
import asyncio
import re

# For QR code scanning (using opencv-python)
try:
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    import webbrowser
    HAS_QR_LIBS = True
except ImportError:
    HAS_QR_LIBS = False

def create_home_screen(app_instance):
    # Card container with spacing between cards
    cards_box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))
    
    # Main container with padding
    home_box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))
    
    # Add some spacing between header and cards
    spacing_box = toga.Box(style=Pack(height=20))
    home_box.add(spacing_box)

    # Header with user info and logout button
    header_box = toga.Box(style=Pack(direction=ROW, padding=10, alignment=CENTER))
    
    # User info
    user = app_instance.auth_service.get_user()
    user_email = user.get('email', 'User') if user else 'User'
    
    user_label = toga.Label(
        f"Hello, {user_email}",
        style=Pack(flex=1, font_size=16, font_weight='bold')
    )
    
    # Logout button
    logout_button = toga.Button(
        "Logout",
        on_press=lambda widget: asyncio.create_task(app_instance.handle_logout()),
        style=Pack(padding=(10, 5), background_color='#f44336', color='white')
    )
    
    header_box.add(user_label)
    header_box.add(logout_button)
    
    # App title
    title_label = toga.Label(
        "Billo Home",
        style=Pack(padding=(10, 10), font_size=24, text_align=CENTER, font_weight='bold')
    )

    # Card 1: Connect to Restaurant with QR Scanner
    async def scan_qr_code(widget):
        if not HAS_QR_LIBS:
            # Show dialog to install dependencies
            install = await app_instance.main_window.confirm_dialog(
                "Dependencies Required",
                "QR code scanning requires additional packages. Install them now?\n\n"
                "This will install: opencv-python, pyzbar, numpy"
            )
            
            if install:
                try:
                    # This would need to be handled properly in a real app
                    # For now, we'll just show instructions
                    await app_instance.main_window.info_dialog(
                        "Install Dependencies",
                        "Please run the following command to install required packages:\n\n"
                        "pip install opencv-python pyzbar numpy"
                    )
                except Exception as e:
                    await app_instance.main_window.error_dialog(
                        "Installation Failed",
                        f"Failed to install dependencies: {str(e)}"
                    )
            return
            
        # Request camera permission
        try:
            from android.permissions import Permission, request_permissions, check_permission
            from android.storage import app_storage_path
            
            # List of required permissions
            required_permissions = [
                Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ]
            
            # Check and request permissions
            def check_and_request_permissions():
                # Check which permissions are needed
                needed_permissions = [
                    perm for perm in required_permissions 
                    if not check_permission(perm)
                ]
                
                if needed_permissions:
                    # Request missing permissions
                    request_permissions(needed_permissions)
                    
                    # Check again after requesting
                    return all(
                        check_permission(perm) 
                        for perm in required_permissions
                    )
                return True
            
            # Check and request permissions
            has_all_permissions = await asyncio.get_event_loop().run_in_executor(
                None, check_and_request_permissions
            )
            
            if not has_all_permissions:
                # If we don't have permissions, show an error and open settings
                open_settings = await app_instance.main_window.confirm_dialog(
                    "Camera Permission Required",
                    "Camera and storage permissions are required to scan QR codes. "
                    "Would you like to open app settings to grant permissions?"
                )
                
                if open_settings:
                    from jnius import autoclass
                    Intent = autoclass('android.content.Intent')
                    Uri = autoclass('android.net.Uri')
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    
                    intent = Intent()
                    intent.setAction('android.settings.APPLICATION_DETAILS_SETTINGS')
                    uri = Uri.fromParts('package', 'com.billo.billo', None)
                    intent.setData(uri)
                    current_activity = PythonActivity.mActivity
                    current_activity.startActivity(intent)
                
                return
                
        except ImportError:
            # Running on a platform without android.permissions, continue with camera access
            pass

        try:
            # Initialize the camera
            cap = cv2.VideoCapture(0)
            
            # Show a dialog while scanning
            scanning = True
            result = None
            
            while scanning:
                # Read frame from camera
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Convert to grayscale for better detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect QR codes
                qr_codes = decode(gray)
                
                if qr_codes:
                    # Get the first detected QR code
                    qr_data = qr_codes[0].data.decode('utf-8')
                    
                    # Check if it's a Billo restaurant QR code
                    if qr_data.startswith(('http://', 'https://')) and 'billo.app' in qr_data:
                        result = qr_data
                        scanning = False
                    else:
                        # Not a Billo QR code, show error
                        await app_instance.main_window.error_dialog(
                            "Invalid QR Code",
                            "Please scan a valid Billo restaurant QR code."
                        )
                        break
                
                # Show the camera preview (optional)
                # cv2.imshow('QR Scanner', frame)
                
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Release the camera
            cap.release()
            cv2.destroyAllWindows()
            
            if result:
                # Open the restaurant PWA URL in the default browser
                webbrowser.open(result)
            
        except Exception as e:
            await app_instance.main_window.error_dialog(
                "Scan Failed",
                f"Failed to scan QR code: {str(e)}"
            )

    # Connect button with padding instead of margin
    connect_button = toga.Button(
        "Scan QR Code to Connect to Restaurant",
        on_press=lambda widget: asyncio.create_task(scan_qr_code(widget)),
        style=Pack(padding=10, height=60, background_color='#4CAF50', color='white')
    )
    
    # Add spacing around the button
    button_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
    button_container.add(connect_button)
    
    # Add a help text below the button
    help_text = toga.Label(
        "Scan the QR code from the restaurant's table or menu to connect",
        style=Pack(padding=(0, 10, 20, 10), text_align=CENTER, color='#666666')
    )

    # Card 2: Saved Restaurants (Initially inactive/disabled)
    # Saved button with padding instead of margin
    saved_button = toga.Button(
        "Saved Restaurants (0)", # Placeholder count
        enabled=False, # Initially inactive
        on_press=lambda widget: print("Saved Restaurants button pressed"), # Placeholder action
        style=Pack(padding=10, height=60)
    )
    
    # Add spacing around the button
    saved_button_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
    saved_button_container.add(saved_button)

    # Add widgets
    home_box.add(header_box)
    home_box.add(toga.Divider(style=Pack(padding_bottom=10)))
    home_box.add(title_label)
    home_box.add(button_container)
    home_box.add(help_text)
    home_box.add(saved_button_container)

    # Potentially add logic here or in app.py to enable saved_button
    # when restaurants are actually saved.

    return home_box
