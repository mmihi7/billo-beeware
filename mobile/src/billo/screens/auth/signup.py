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

    # Validation functions
    def is_valid_email(email):
        import re
        return bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))

    def update_field_style(field, is_valid):
        field.style.background_color = "#ffebee" if not is_valid else "#e8f5e9"
        return is_valid

    # Form fields with validation
    name_input = toga.TextInput(
        placeholder="Full Name", 
        style=Pack(padding=5, width=300)
    )
    
    email_input = toga.TextInput(
        placeholder="Email", 
        style=Pack(padding=5, width=300)
    )
    
    password_input = toga.PasswordInput(
        placeholder="Password (min 6 characters)", 
        style=Pack(padding=5, width=300)
    )
    
    confirm_password_input = toga.PasswordInput(
        placeholder="Confirm Password", 
        style=Pack(padding=5, width=300)
    )
    
    def validate_form():
        # Validate name
        name_valid = bool(name_input.value.strip())
        update_field_style(name_input, name_valid)
        
        # Validate email
        email_valid = is_valid_email(email_input.value)
        update_field_style(email_input, email_valid)
        
        # Validate password
        password_valid = len(password_input.value or '') >= 6
        update_field_style(password_input, password_valid)
        
        # Validate password match
        passwords_match = (password_input.value == confirm_password_input.value) and password_input.value
        update_field_style(confirm_password_input, passwords_match)
        
        # Enable/disable signup button
        signup_button.enabled = all([name_valid, email_valid, password_valid, passwords_match])
        
        return signup_button.enabled
    
    # Set up change handlers for all fields
    def on_field_change(widget):
        validate_form()
    
    for field in [name_input, email_input, password_input, confirm_password_input]:
        field.on_change = on_field_change

    # Sign up button handler
    def handle_signup(widget):
        # First validate the form
        if not validate_form():
            app_instance.show_error("Validation Error", "Please fill in all fields correctly.")
            return
            
        # Create a callback for when the signup completes
        def on_signup_done(future):
            try:
                success = future.result()
                if success:
                    # Clear form on success
                    name_input.value = ""
                    email_input.value = ""
                    password_input.value = ""
                    confirm_password_input.value = ""
            except Exception as e:
                app_instance.show_error("Signup Failed", f"An error occurred: {str(e)}")
        
        # Start the signup process
        future = asyncio.run_coroutine_threadsafe(
            app_instance.handle_signup(
                name_input.value.strip(),
                email_input.value.strip(),
                password_input.value,
                confirm_password_input.value
            ),
            asyncio.get_event_loop()
        )
        future.add_done_callback(on_signup_done)
    
    signup_button = toga.Button(
        "Sign Up",
        on_press=handle_signup,
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
