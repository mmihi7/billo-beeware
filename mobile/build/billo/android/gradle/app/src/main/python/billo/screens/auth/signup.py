# src/billo/screens/auth/signup.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

def create_signup_screen(app_instance):
    # Main container
    signup_box = toga.Box(style=Pack(
        direction=COLUMN,
        padding=20,
        alignment=CENTER,
        flex=1
    ))

    # Title
    title_label = toga.Label(
        "Create Account",
        style=Pack(
            padding=(0, 0, 20, 0),
            font_size=24,
            text_align=CENTER,
            flex=0
        )
    )

    # Form fields
    name_input = toga.TextInput(placeholder="Full Name", style=Pack(padding=5, width=300))
    email_input = toga.TextInput(placeholder="Email", style=Pack(padding=5, width=300))
    password_input = toga.PasswordInput(placeholder="Password", style=Pack(padding=5, width=300))
    confirm_password_input = toga.PasswordInput(
        placeholder="Confirm Password", 
        style=Pack(padding=5, width=300)
    )

    # Sign up button
    signup_button = toga.Button(
        "Sign Up",
        on_press=lambda widget: app_instance.handle_signup(
            name_input.value,
            email_input.value,
            password_input.value,
            confirm_password_input.value
        ),
        style=Pack(padding=(20, 10, 10, 10), width=300)
    )

    # Link to sign in
    signin_link = toga.Button(
        "Already have an account? Sign In",
        on_press=lambda widget: app_instance.show_signin_screen(),
        style=Pack(padding=10, color='#1E88E5')
    )

    # Add all widgets to the box
    signup_box.add(title_label)
    signup_box.add(name_input)
    signup_box.add(email_input)
    signup_box.add(password_input)
    signup_box.add(confirm_password_input)
    # Add signup button with spacing
    signup_box.add(signup_button)
    
    # Add some spacing before the signin link
    spacing_box = toga.Box(style=Pack(height=10))
    signup_box.add(spacing_box)
    
    # Add signin link
    signup_box.add(signin_link)

    return signup_box
