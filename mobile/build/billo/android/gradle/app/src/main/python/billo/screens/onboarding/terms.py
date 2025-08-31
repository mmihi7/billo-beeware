# src/billo/screens/onboarding/terms.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT

def create_terms_screen(app_instance):
    # Main container with increased padding for better spacing
    terms_box = toga.Box(style=Pack(
        direction=COLUMN,
        padding=30,
        alignment=CENTER,
        flex=1
    ))

    # Title with bottom padding for spacing
    title_label = toga.Label(
        "Terms & Conditions",
        style=Pack(
            padding=(0, 0, 30, 0),  # Increased bottom padding
            font_size=24,
            text_align=CENTER,
            flex=0
        )
    )

    # Terms content
    terms_content = toga.ScrollContainer(style=Pack(flex=1))
    
    terms_text = (
        "By using Billo, you agree to our Terms of Service and Privacy Policy.\n\n"
        "1. We respect your privacy and handle your data securely.\n"
        "2. We require camera access for QR code scanning.\n"
        "3. We need internet access to sync your data.\n\n"
        "Please review our full terms at billo.app/terms"
    )
    
    terms_label = toga.Label(
        terms_text,
        style=Pack(
            padding=10,
            text_align=LEFT,
            width=300
        )
    )
    
    terms_content.content = terms_label

    # Accept button
    accept_button = toga.Button(
        "I Accept",
        on_press=lambda widget: app_instance.show_signup_screen(),
        style=Pack(
            padding=(30, 15, 15, 15),  # Increased top padding for spacing
            width=300,
            background_color='#1E88E5',
            color='white'
        )
    )

    # Add all widgets to the box
    terms_box.add(title_label)
    terms_box.add(terms_content)
    terms_box.add(accept_button)

    return terms_box
