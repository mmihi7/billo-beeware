// Initialize quantities from data attributes
document.addEventListener('DOMContentLoaded', () => {
    // Get menu items from data attribute
    const menuItems = JSON.parse(document.getElementById('menu-data').dataset.items);
    const quantities = {};
    
    // Initialize quantities
    menuItems.forEach(item => {
        quantities[item.id] = 0;
    });
    
    // Update quantity for an item
    window.updateQuantity = function(itemId, change) {
        const newQuantity = Math.max(0, (quantities[itemId] || 0) + change);
        quantities[itemId] = newQuantity;
        
        // Update UI
        const quantityDisplay = document.getElementById(`quantity-${itemId}`);
        const addButton = document.getElementById(`add-btn-${itemId}`);
        
        if (quantityDisplay) {
            quantityDisplay.textContent = newQuantity;
            quantityDisplay.style.display = newQuantity > 0 ? 'inline-block' : 'none';
        }
        
        if (addButton) {
            addButton.style.display = newQuantity > 0 ? 'none' : 'inline-flex';
        }
        
        // Update cart summary
        updateCartSummary(quantities, menuItems);
    };
    
    // Update cart summary
    function updateCartSummary(quantities, items) {
        const cartItems = [];
        let total = 0;
        
        Object.entries(quantities).forEach(([id, qty]) => {
            if (qty > 0) {
                const item = items.find(i => i.id === id);
                if (item) {
                    const itemTotal = item.price * qty;
                    cartItems.push({ ...item, quantity: qty, itemTotal });
                    total += itemTotal;
                }
            }
        });
        
        // Update cart items list
        const cartItemsContainer = document.getElementById('cart-items');
        if (cartItemsContainer) {
            if (cartItems.length === 0) {
                cartItemsContainer.innerHTML = '<p class="text-gray-500">Your cart is empty</p>';
            } else {
                cartItemsContainer.innerHTML = cartItems.map(item => `
                    <div class="flex items-center justify-between py-2 border-b border-gray-100">
                        <div>
                            <div class="font-medium">${item.name}</div>
                            <div class="text-sm text-gray-500">${formatCurrency(item.price)} × ${item.quantity}</div>
                        </div>
                        <div class="flex items-center">
                            <span class="mr-4">${formatCurrency(item.itemTotal)}</span>
                            <button onclick="updateQuantity('${item.id}', -1)" class="text-gray-500 hover:text-red-500">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        }
        
        // Update total
        const cartTotal = document.getElementById('cart-total');
        if (cartTotal) {
            cartTotal.textContent = formatCurrency(total);
        }
    }
    
    // Format currency
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: 'KES',
            minimumFractionDigits: 2
        }).format(amount / 100);
    }
});
