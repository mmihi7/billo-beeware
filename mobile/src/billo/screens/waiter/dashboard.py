import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, Pack
from toga.icons import Icon

class WaiterDashboard:
    def __init__(self, app):
        self.app = app
        self.orders = []
        self.notifications = []
        
        # Main container
        self.box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        # Header
        header = toga.Box(style=Pack(direction=ROW, padding=10, background_color='#1e88e5'))
        self.header_label = toga.Label(
            "Waiter Dashboard",
            style=Pack(color='white', font_size=18, flex=1)
        )
        
        # Notification bell
        self.notification_btn = toga.Button(
            "🔔",
            on_press=self.show_notifications,
            style=Pack(width=40, height=40, padding=5)
        )
        
        header.add(self.header_label)
        header.add(self.notification_btn)
        
        # Tabs for different order statuses
        self.tabs = toga.OptionContainer(
            style=Pack(flex=1)
        )
        
        # Create tabs for different order statuses
        self.active_orders_tab = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.ready_orders_tab = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.completed_orders_tab = toga.Box(style=Pack(direction=COLUMN, padding=5))
        
        self.tabs.add("Active Orders", self.active_orders_tab)
        self.tabs.add("Ready", self.ready_orders_tab)
        self.tabs.add("Completed", self.completed_orders_tab)
        
        # Add components to main box
        self.box.add(header)
        self.box.add(self.tabs)
        
        # Load initial data
        self.load_orders()
    
    def load_orders(self):
        """Load orders from the API"""
        # TODO: Implement API call to fetch orders
        # For now, using mock data
        self.orders = [
            {"id": "1", "table": "T-01", "items": ["Pizza", "Coke"], "status": "active"},
            {"id": "2", "table": "T-03", "items": ["Burger", "Fries"], "status": "ready"},
            {"id": "3", "table": "T-05", "items": ["Pasta"], "status": "completed"},
        ]
        self.update_orders_display()
    
    def update_orders_display(self):
        """Update the UI with the current orders"""
        # Clear existing orders
        self.active_orders_tab.remove_all_children()
        self.ready_orders_tab.remove_all_children()
        self.completed_orders_tab.remove_all_join()
        
        # Add orders to respective tabs
        for order in self.orders:
            order_card = self.create_order_card(order)
            if order["status"] == "active":
                self.active_orders_tab.add(order_card)
            elif order["status"] == "ready":
                self.ready_orders_tab.add(order_card)
            else:
                self.completed_orders_tab.add(order_card)
    
    def create_order_card(self, order):
        """Create a card for an order"""
        card = toga.Box(style=Pack(
            direction=COLUMN, 
            padding=10, 
            background_color='white',
            margin_bottom=5
        ))
        
        # Header with table number and status
        header = toga.Box(style=Pack(direction=ROW, padding_bottom=5))
        header.add(toga.Label(
            f"Table {order['table']}",
            style=Pack(flex=1, font_weight='bold')
        ))
        header.add(toga.Label(
            order["status"].upper(),
            style=Pack(color='gray')
        ))
        
        # Order items
        items = toga.Box(style=Pack(direction=COLUMN, padding_left=10))
        for item in order["items"]:
            items.add(toga.Label(f"• {item}"))
        
        # Action buttons
        actions = toga.Box(style=Pack(direction=ROW, padding_top=5))
        
        if order["status"] == "active":
            actions.add(toga.Button(
                "Mark Ready",
                on_press=lambda w, o=order: self.update_order_status(o["id"], "ready"),
                style=Pack(flex=1, margin_right=5, background_color='#4caf50')
            ))
        elif order["status"] == "ready":
            actions.add(toga.Button(
                "Mark Delivered",
                on_press=lambda w, o=order: self.update_order_status(o["id"], "completed"),
                style=Pack(flex=1, background_color='#2196f3')
            ))
        
        card.add(header)
        card.add(items)
        if len(actions.children) > 0:
            card.add(actions)
        
        return card
    
    def update_order_status(self, order_id, new_status):
        """Update the status of an order"""
        # TODO: Implement API call to update order status
        for order in self.orders:
            if order["id"] == order_id:
                order["status"] = new_status
                break
        self.update_orders_display()
    
    def show_notifications(self, widget):
        """Show notifications dialog"""
        # TODO: Implement notifications view
        self.app.main_window.info_dialog("Notifications", "No new notifications")

def create_waiter_dashboard(app):
    """Factory function to create the waiter dashboard"""
    return WaiterDashboard(app).box
