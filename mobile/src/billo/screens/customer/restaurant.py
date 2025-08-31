import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, BOLD
from toga.constants import CENTER as ALIGN_CENTER

class RestaurantScreen:
    def __init__(self, tab_number, restaurant_name):
        self.tab_number = tab_number
        self.restaurant_name = restaurant_name
        
    def create(self):
        # Main container
        main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=10))
        
        # Header with tab number and restaurant name
        header = toga.Box(style=Pack(direction=COLUMN, margin_bottom=10))
        tab_label = toga.Label(
            f"Tab {self.tab_number}",
            style=Pack(font_size=24, font_weight=BOLD, text_align=CENTER, margin_bottom=5)
        )
        name_label = toga.Label(
            self.restaurant_name,
            style=Pack(font_size=18, text_align=CENTER, margin_bottom=10)
        )
        header.add(tab_label)
        header.add(name_label)
        
        # Advertisement placeholder
        ad_box = toga.Box(
            style=Pack(height=100, background_color="#f0f0f0", margin=10)
        )
        ad_label = toga.Label(
            "Advertisement",
            style=Pack(text_align=CENTER, width=200, padding_top=35)
        )
        ad_box.add(ad_label)
        
        # Orders list (placeholder)
        orders_label = toga.Label(
            "Your Orders",
            style=Pack(font_weight=BOLD, margin_bottom=5)
        )
        orders_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        # Sample order items (replace with actual data)
        order_items = [
            "1x Pizza Margherita - KES 1200",
            "2x Soda - KES 200"
        ]
        
        for item in order_items:
            order_item = toga.Label(item, style=Pack(margin_bottom=5))
            orders_box.add(order_item)
        
        # Total price
        total_label = toga.Label(
            "Total: KES 1400",
            style=Pack(font_weight=BOLD, margin_top=10, margin_bottom=10)
        )
        
        # Payment button
        pay_button = toga.Button(
            "Pay Now",
            on_press=self.on_pay,
            style=Pack(margin=15, padding=10, background_color="#4CAF50", color="white")
        )
        
        # Message input
        message_input = toga.TextInput(
            placeholder="Add a note for your order...",
            style=Pack(flex=1, margin=10)
        )
        
        # Add all components to main box
        main_box.add(header)
        main_box.add(ad_box)
        main_box.add(orders_label)
        main_box.add(orders_box)
        main_box.add(total_label)
        main_box.add(pay_button)
        main_box.add(message_input)
        
        return main_box
    
    def on_pay(self, widget):
        # Handle payment logic here
        print("Initiating payment...")
