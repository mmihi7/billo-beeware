# src/billo/screens/auth/signin.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER

def create_signin_screen(app_instance):
    # Main container
    signin_box = toga.Box(style=Pack(
        direction=COLUMN,
        padding=20,
        alignment=CENTER,
        flex=1
    ))

    # Title
    title_label = toga.Label(
        "Welcome Back",
        style=Pack(
            padding=(0, 0, 20, 0),
            font_size=24,
            text_align=CENTER,
            flex=0
        )
    )

    # Form fields
    email_input = toga.TextInput(placeholder="Email", style=Pack(padding=5, width=300))
    password_input = toga.PasswordInput(placeholder="Password", style=Pack(padding=5, width=300))

    # Forgot password link
    forgot_password = toga.Button(
        "Forgot Password?",
        on_press=lambda widget: app_instance.show_forgot_password(),
        style=Pack(padding=5, color='#1E88E5')
    )

    # Sign in button with increased top padding
    signin_button = toga.Button(
        "Sign In",
        on_press=lambda widget: app_instance.handle_signin(
            email_input.value,
            password_input.value
        ),
        style=Pack(padding=(20, 10, 10, 10), width=300)  # Increased top padding
    )

    # Link to sign up
    signup_link = toga.Button(
        "Don't have an account? Sign Up",
        on_press=lambda widget: app_instance.show_signup_screen(),
        style=Pack(padding=10, color='#1E88E5')
    )

    # Add all widgets to the box with proper spacing
    signin_box.add(title_label)
    
    # Add spacing between form elements
    def add_with_spacing(box, widget, top_padding=10):
        if top_padding > 0:
            spacer = toga.Box(style=Pack(height=top_padding))
            box.add(spacer)
        box.add(widget)
    
    add_with_spacing(signin_box, email_input)
    add_with_spacing(signin_box, password_input, 5)
    add_with_spacing(signin_box, forgot_password, 5)
    add_with_spacing(signin_box, signin_button, 10)
    add_with_spacing(signin_box, signup_link, 5)

    return signin_box
