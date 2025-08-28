# src/billo/screens/onboarding/terms.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, PADDED

def create_terms_screen(app_instance):
    terms_box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))

    title_label = toga.Label(
        "Permissions Required",
        style=Pack(padding=(10, 10), font_size=18, text_align=CENTER, flex=0) # flex=0 for title
    )

    # Simple text explanation (you'd expand this significantly)
    terms_text = (
        "Billo needs access to the internet to connect to restaurants "
        "and the camera to scan QR codes.\n\n"
        "Please accept these permissions to continue."
    )
    terms_label = toga.Label(
        terms_text,
        style=Pack(padding=10, text_align=LEFT, flex=1) # flex=1 to take space
    )

    # Placeholder for actual permission requests
    # In a real app, you'd integrate platform-specific permission handling here
    # For now, we simulate acceptance.
    permissions_status = toga.Label(
        "Internet Access: Granted\nCamera Access: Granted (Simulated)",
        style=Pack(padding=10, text_align=CENTER, color='green')
    )

    accept_button = toga.Button(
        "Accept & Continue",
        on_press=lambda widget: app_instance.show_home_screen(), # Method in app.py
        style=Pack(padding=10, width=200)
    )

    terms_box.add(title_label)
    terms_box.add(terms_label)
    terms_box.add(permissions_status)
    terms_box.add(accept_button)

    return terms_box
