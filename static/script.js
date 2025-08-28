class ShoppingList {
    constructor() {
        this.items = [];
        this.loadingEl = document.getElementById('loading');
        this.errorEl = document.getElementById('error');
        this.listEl = document.getElementById('shopping-list');
        this.newItemInput = document.getElementById('new-item');
        this.addBtn = document.getElementById('add-btn');
        
        this.bindEvents();
        this.loadItems();
    }
    
    bindEvents() {
        this.addBtn.addEventListener('click', () => this.addItem());
        this.newItemInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addItem();
        });
    }
    
    showLoading(show) {
        this.loadingEl.style.display = show ? 'block' : 'none';
    }
    
    showError(message) {
        this.errorEl.textContent = message;
        this.errorEl.style.display = message ? 'block' : 'none';
    }
    
    async apiCall(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error(`HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            this.showError(`Error: ${error.message}`);
            throw error;
        }
    }
    
    async loadItems() {
        this.showLoading(true);
        try {
            this.items = await this.apiCall('/api/items');
            this.renderItems();
        } catch (error) {
            console.error('Failed to load items:', error);
        } finally {
            this.showLoading(false);
        }
    }
    
    async addItem() {
        const name = this.newItemInput.value.trim();
        if (!name) return;
        
        try {
            const newItem = await this.apiCall('/api/items', {
                method: 'POST',
                body: JSON.stringify({ name })
            });
            
            this.items.push(newItem);
            this.newItemInput.value = '';
            this.renderItems();
        } catch (error) {
            console.error('Failed to add item:', error);
        }
    }
    
    async updateItem(id, name) {
        try {
            await this.apiCall(`/api/items/${id}`, {
                method: 'PUT',
                body: JSON.stringify({ name })
            });
            
            const item = this.items.find(i => i.id === id);
            if (item) item.name = name;
            this.renderItems();
        } catch (error) {
            console.error('Failed to update item:', error);
        }
    }
    
    async toggleItem(id) {
        try {
            await this.apiCall(`/api/items/${id}/toggle`, {
                method: 'PUT'
            });
            
            const item = this.items.find(i => i.id === id);
            if (item) item.completed = !item.completed;
            this.renderItems();
        } catch (error) {
            console.error('Failed to toggle item:', error);
        }
    }
    
    async deleteItem(id) {
        if (!confirm('Delete this item?')) return;
        
        try {
            await this.apiCall(`/api/items/${id}`, {
                method: 'DELETE'
            });
            
            this.items = this.items.filter(i => i.id !== id);
            this.renderItems();
        } catch (error) {
            console.error('Failed to delete item:', error);
        }
    }
    
    renderItems() {
        if (this.items.length === 0) {
            this.listEl.innerHTML = '<div class="empty-state">No items yet. Add your first shopping item above!</div>';
            return;
        }
        
        // Sort items: uncompleted first, then by creation date
        const sortedItems = [...this.items].sort((a, b) => {
            if (a.completed !== b.completed) {
                return a.completed - b.completed;
            }
            return new Date(b.created_at) - new Date(a.created_at);
        });
        
        this.listEl.innerHTML = sortedItems.map(item => `
            <div class="item ${item.completed ? 'completed' : ''}">
                <input type="checkbox" 
                       class="item-checkbox" 
                       ${item.completed ? 'checked' : ''} 
                       onchange="app.toggleItem(${item.id})">
                <span class="item-text" 
                      contenteditable="true" 
                      data-id="${item.id}"
                      onblur="app.handleTextEdit(this)"
                      onkeypress="app.handleTextKeypress(event, this)">${item.name}</span>
                <div class="item-actions">
                    <button class="btn btn-danger" onclick="app.deleteItem(${item.id})">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    handleTextEdit(element) {
        const id = parseInt(element.dataset.id);
        const newName = element.textContent.trim();
        
        if (!newName) {
            this.renderItems(); // Reset if empty
            return;
        }
        
        const item = this.items.find(i => i.id === id);
        if (item && item.name !== newName) {
            this.updateItem(id, newName);
        }
    }
    
    handleTextKeypress(event, element) {
        if (event.key === 'Enter') {
            element.blur();
            event.preventDefault();
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ShoppingList();
});