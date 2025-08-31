import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from toga.icons import Icon

class RestaurantDashboard:
    def __init__(self, app):
        self.app = app
        self.menu_categories = []
        self.menu_items = {}
        self.current_order = []
        
        # Main container with padding
        self.box = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))
        
        # Header with restaurant name and cart
        self.header = toga.Box(style=Pack(direction=ROW, padding=15, background_color='#0d47a1'))
        
        # Restaurant title
        self.title_label = toga.Label(
            "Restaurant Dashboard",
            style=Pack(color='white', font_size=16, font_weight='bold', flex=1)
        )
        
        # Cart button with badge
        self.cart_btn = toga.Button(
            "🛒 0",
            on_press=self.show_cart,
            style=Pack(width=60, height=40, padding=5, background_color='#1565c0')
        )
        
        # Add widgets to header
        self.header.add(self.title_label)
        self.header.add(self.cart_btn)
        
        # Create a table for menu items with padding
        self.table = toga.Table(
            headings=['Name', 'Price', 'Description', 'Action'],
            style=Pack(flex=1, padding=5),
            on_select=self.on_item_selected
        )
        
        # Add loading indicator with proper spacing
        self.loading_box = toga.Box(style=Pack(direction=COLUMN, alignment='center', flex=1, padding=20))
        self.loading_box.add(toga.Label("Loading menu...", style=Pack(padding=20)))
        
        # Cart view (initially hidden)
        self.cart_view = self.create_cart_view()
        self.cart_view.style.update(visibility='hidden')
        
        # Create a scrollable container for the content
        scroll_box = toga.ScrollContainer(content=self.table, style=Pack(flex=1))
        
        # Main content box (menu or cart)
        self.content_box = toga.Box(children=[self.loading_box], style=Pack(direction=COLUMN, flex=1))
        
        # Add components to main box
        self.box.add(self.header)
        self.content_box.style.flex = 1
        self.box.add(self.content_box)
        
        # Load menu data
        self.load_menu()
    
    def load_menu(self):
        """Load menu data from the API"""
        # TODO: Replace with actual API call
        # Mock data for now
        self.menu_categories = ["Starters", "Main Course", "Desserts", "Drinks"]
        self.menu_items = {
            "Starters": [
                {"id": "s1", "name": "Bruschetta", "price": 8.99, "description": "Toasted bread with tomatoes"},
                {"id": "s2", "name": "Calamari", "price": 12.99, "description": "Fried squid with aioli"}
            ],
            "Main Course": [
                {"id": "m1", "name": "Pasta Carbonara", "price": 15.99, "description": "Classic Italian pasta"},
                {"id": "m2", "name": "Grilled Salmon", "price": 22.99, "description": "Fresh salmon with vegetables"}
            ],
            "Desserts": [
                {"id": "d1", "name": "Tiramisu", "price": 7.99, "description": "Classic Italian dessert"},
                {"id": "d2", "name": "Chocolate Lava Cake", "price": 8.99, "description": "Warm chocolate cake with ice cream"}
            ],
            "Drinks": [
                {"id": "dr1", "name": "Soda", "price": 2.99, "description": "Cola, Lemonade, or Orange"},
                {"id": "dr2", "name": "Wine", "price": 8.99, "description": "House red or white"}
            ]
        }
        
        self.update_menu_display()
    
    def on_item_selected(self, widget, row):
        """Handle item selection"""
        if row:
            print(f"Selected: {row.name}")
    
    def update_menu_display(self):
        """Update the UI with the menu"""
        # Clear existing data
        self.table.data.clear()
        
        # Add items to the table
        for category in self.menu_categories:
            for item in self.menu_items.get(category, []):
                self.table.data.append([
                    item['name'],
                    f"${item['price']:.2f}",
                    item['description'],
                    "Add to Cart"
                ])
        
        # Update the content box
        if self.loading_box in self.content_box.children:
            self.content_box.remove(self.loading_box)
        
        # Clear existing content and add the table
        for child in self.content_box.children[:]:
            self.content_box.remove(child)
        self.content_box.add(self.table)
    
    def create_menu_item_card(self, item):
        """Create a card for a menu item"""
        card = toga.Box(style=Pack(
            direction=COLUMN, 
            padding=10, 
            background_color='white',
            margin_bottom=5
        ))
        
        # Item name and price
        header = toga.Box(style=Pack(direction=ROW, padding_bottom=5))
        header.add(toga.Label(
            item["name"],
            style=Pack(flex=1, font_weight='bold')
        ))
        header.add(toga.Label(
            f"${item['price']:.2f}",
            style=Pack(font_weight='bold')
        ))
        
        # Item description
        description = toga.Label(
            item["description"],
            style=Pack(font_size=12, color='gray', padding_bottom=5)
        )
        
        # Add to order button
        add_btn = toga.Button(
            "Add to Order",
            on_press=lambda w, i=item: self.add_to_order(i),
            style=Pack(background_color='#4caf50', color='white')
        )
        
        card.add(header)
        card.add(description)
        card.add(add_btn)
        
        return card
    
    def create_cart_view(self):
        """Create the cart view"""
        cart_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        # Cart items will be added here
        self.cart_items_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        # Total and checkout button
        self.cart_total = toga.Label("Total: $0.00", 
                                   style=Pack(font_size=16, font_weight='bold', padding=10))
        
        checkout_btn = toga.Button(
            "Checkout",
            on_press=self.checkout,
            style=Pack(background_color='#1e88e5', color='white', padding=10)
        )
        
        cart_box.add(toga.Label("Your Order", style=Pack(font_size=18, padding=10)))
        cart_box.add(self.cart_items_box)
        cart_box.add(toga.Divider(style=Pack(padding=5)))
        cart_box.add(self.cart_total)
        cart_box.add(checkout_btn)
        
        return cart_box
    
    def add_to_order(self, item):
        """Add an item to the current order"""
        self.current_order.append(item)
        self.update_cart_badge()
        self.show_toast(f"Added {item['name']} to order")
    
    def update_cart_badge(self):
        """Update the cart badge with the number of items"""
        self.cart_btn.text = f"🛒 {len(self.current_order)}"
        self.update_cart_view()
    
    def update_cart_view(self):
        """Update the cart view with current order items"""
        # Clear existing items
        self.cart_items_box.remove_all_children()
        
        # Add each item in the cart
        total = 0
        for item in self.current_order:
            item_box = toga.Box(style=Pack(direction=ROW, padding=5))
            item_box.add(toga.Label(
                f"{item['name']} - ${item['price']:.2f}",
                style=Pack(flex=1)
            ))
            
            # Remove button
            remove_btn = toga.Button(
                "Remove",
                on_press=lambda w, i=item: self.remove_from_order(i),
                style=Pack(background_color='#f44336', color='white')
            )
            item_box.add(remove_btn)
            
            self.cart_items_box.add(item_box)
            total += item['price']
        
        # Update total
        self.cart_total.text = f"Total: ${total:.2f}"
    
    def remove_from_order(self, item):
        """Remove an item from the current order"""
        if item in self.current_order:
            self.current_order.remove(item)
            self.update_cart_badge()
    
    def show_cart(self, widget):
        """Toggle between menu and cart view"""
        if self.tabs in self.content_box.children:
            # Show cart
            self.content_box.remove(self.tabs)
            self.cart_view.style.update(visibility='visible')
            self.title_label.text = "Your Order"
        else:
            # Show menu
            self.content_box.add(self.tabs)
            self.cart_view.style.update(visibility='hidden')
            self.title_label.text = "Restaurant Name"
    
    def checkout(self, widget):
        """Process the order"""
        if not self.current_order:
            self.show_toast("Your cart is empty!")
            return
            
        # TODO: Implement actual checkout process
        self.app.main_window.confirm_dialog(
            "Confirm Order",
            f"Place order for ${sum(item['price'] for item in self.current_order):.2f}?",
            on_result=self.process_order
        )
    
    def process_order(self, dialog, result):
        """Process the order after confirmation"""
        if result:
            # TODO: Send order to server
            self.show_toast("Order placed successfully!")
            self.current_order = []
            self.update_cart_badge()
            self.show_cart(None)  # Return to menu
    
    def show_toast(self, message):
        """Show a toast message"""
        self.app.main_window.info_dialog("Billo", message)

def create_restaurant_dashboard(app):
    """Factory function to create the restaurant dashboard"""
    return RestaurantDashboard(app).box
