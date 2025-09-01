class ShoppingList {
    constructor() {
        this.items = [];
        this.init();
    }

    init() {
        this.initTheme();
        this.bindEvents();
        this.loadItems();
    }

    initTheme() {
        // Get saved theme or default to dark
        const savedTheme = localStorage.getItem('shopping-list-theme') || 'dark';
        this.setTheme(savedTheme);
    }

    setTheme(theme) {
        const body = document.body;
        const themeIcon = document.getElementById('themeIcon');
        
        if (theme === 'light') {
            body.setAttribute('data-theme', 'light');
            if (themeIcon) themeIcon.textContent = '🌞';
        } else {
            body.removeAttribute('data-theme');
            if (themeIcon) themeIcon.textContent = '🌙';
        }
        
        localStorage.setItem('shopping-list-theme', theme);
    }

    toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    bindEvents() {
        const itemInput = document.getElementById('itemInput');
        const addBtn = document.getElementById('addBtn');
        const clearCompletedBtn = document.getElementById('clearCompletedBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const themeToggle = document.getElementById('themeToggle');

        // Add item events
        addBtn.addEventListener('click', () => this.addItem());
        itemInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addItem();
            }
        });

        // Clear completed items
        clearCompletedBtn.addEventListener('click', () => this.clearCompleted());
        
        // Logout
        logoutBtn.addEventListener('click', () => this.logout());
        
        // Theme toggle
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    async loadItems() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/items');
            if (!response.ok) throw new Error('Failed to load items');
            
            this.items = await response.json();
            this.renderItems();
            this.updateItemCount();
        } catch (error) {
            this.showError('Failed to load shopping list');
        } finally {
            this.showLoading(false);
        }
    }

    async addItem() {
        const input = document.getElementById('itemInput');
        const name = input.value.trim();
        
        if (!name) return;

        try {
            const response = await fetch('/api/items', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name })
            });

            if (!response.ok) throw new Error('Failed to add item');
            
            const newItem = await response.json();
            this.items.push(newItem);
            input.value = '';
            this.renderItems();
            this.updateItemCount();
            
        } catch (error) {
            this.showError('Failed to add item');
        }
    }

    async updateItem(id, updates) {
        try {
            const response = await fetch(`/api/items/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updates)
            });

            if (!response.ok) throw new Error('Failed to update item');
            
            // Update local item
            const item = this.items.find(item => item.id === id);
            if (item) {
                Object.assign(item, updates);
                this.renderItems();
                this.updateItemCount();
            }
            
        } catch (error) {
            this.showError('Failed to update item');
        }
    }

    async deleteItem(id) {
        try {
            const response = await fetch(`/api/items/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete item');
            
            this.items = this.items.filter(item => item.id !== id);
            this.renderItems();
            this.updateItemCount();
            
        } catch (error) {
            this.showError('Failed to delete item');
        }
    }

    async clearCompleted() {
        const completedCount = this.items.filter(item => item.completed).length;
        if (completedCount === 0) return;

        if (!confirm(`Remove ${completedCount} completed item${completedCount > 1 ? 's' : ''}?`)) {
            return;
        }

        try {
            const response = await fetch('/api/items/clear-completed', {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to clear completed items');
            
            this.items = this.items.filter(item => !item.completed);
            this.renderItems();
            this.updateItemCount();
            
        } catch (error) {
            this.showError('Failed to clear completed items');
        }
    }

    renderItems() {
        const listElement = document.getElementById('shoppingList');
        
        if (this.items.length === 0) {
            listElement.innerHTML = '';
            return;
        }

        listElement.innerHTML = this.items.map(item => `
            <li class="list-item ${item.completed ? 'completed' : ''}" data-id="${item.id}">
                <input 
                    type="checkbox" 
                    class="item-checkbox" 
                    ${item.completed ? 'checked' : ''}
                    onchange="shoppingList.toggleComplete(${item.id})"
                >
                <input 
                    type="text" 
                    class="item-text" 
                    value="${this.escapeHtml(item.name)}"
                    onblur="shoppingList.updateItemName(${item.id}, this.value)"
                    onkeypress="if(event.key==='Enter') this.blur()"
                >
                <button 
                    class="delete-btn" 
                    onclick="shoppingList.deleteItem(${item.id})"
                    title="Delete item"
                >
                    ✕
                </button>
            </li>
        `).join('');
    }

    toggleComplete(id) {
        const item = this.items.find(item => item.id === id);
        if (item) {
            this.updateItem(id, { completed: !item.completed });
        }
    }

    updateItemName(id, newName) {
        const trimmedName = newName.trim();
        const item = this.items.find(item => item.id === id);
        
        if (!item) return;
        
        if (!trimmedName) {
            // Restore original name if empty
            this.renderItems();
            return;
        }
        
        if (trimmedName !== item.name) {
            this.updateItem(id, { name: trimmedName });
        }
    }

    updateItemCount() {
        const totalCount = this.items.length;
        const completedCount = this.items.filter(item => item.completed).length;
        const pendingCount = totalCount - completedCount;
        
        const countElement = document.getElementById('itemCount');
        if (totalCount === 0) {
            countElement.textContent = 'No items';
        } else if (completedCount === 0) {
            countElement.textContent = `${totalCount} item${totalCount > 1 ? 's' : ''}`;
        } else {
            countElement.textContent = `${pendingCount} pending, ${completedCount} done`;
        }
    }

    showLoading(show) {
        const loadingElement = document.getElementById('loading');
        loadingElement.style.display = show ? 'block' : 'none';
    }

    showError(message) {
        const errorElement = document.getElementById('error');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Hide error after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async logout() {
        if (!confirm('Are you sure you want to logout?')) {
            return;
        }

        try {
            // Make a request to the logout endpoint to clear session
            const response = await fetch('/logout');
            
            // Redirect to login page (logout endpoint handles session clearing)
            window.location.href = '/login';
        } catch (error) {
            // If request fails, still redirect to login page
            window.location.href = '/login';
        }
    }
}

// Initialize the shopping list when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.shoppingList = new ShoppingList();
});