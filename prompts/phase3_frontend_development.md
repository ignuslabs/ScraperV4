# Phase 3: Frontend Development
## Advanced Web Interface with Modern JavaScript

### Overview
Build a sophisticated web interface using Eel for Python-JavaScript integration, featuring real-time progress monitoring, component-based architecture, and comprehensive data visualization.

### Architecture Components

#### 3.1 Frontend Structure
```
web/
├── static/
│   ├── css/
│   │   ├── main.css
│   │   ├── components.css
│   │   └── themes.css
│   ├── js/
│   │   ├── components/
│   │   │   ├── scraper-dashboard.js
│   │   │   ├── task-monitor.js
│   │   │   ├── data-viewer.js
│   │   │   └── export-manager.js
│   │   ├── utils/
│   │   │   ├── api-client.js
│   │   │   ├── websocket-manager.js
│   │   │   └── data-formatter.js
│   │   └── main.js
│   └── assets/
│       ├── icons/
│       └── images/
└── templates/
    ├── index.html
    ├── dashboard.html
    └── components/
        ├── header.html
        ├── sidebar.html
        └── modals.html
```

#### 3.2 Core Frontend Components

**Main Dashboard Component (scraper-dashboard.js)**
```javascript
class ScraperDashboard {
    constructor() {
        this.taskMonitor = new TaskMonitor();
        this.dataViewer = new DataViewer();
        this.exportManager = new ExportManager();
        this.wsManager = new WebSocketManager();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.initializeWebSocket();
    }

    setupEventListeners() {
        // New scraping task
        document.getElementById('start-scrape-btn').addEventListener('click', () => {
            this.startScrapingTask();
        });

        // Task management
        document.getElementById('pause-all-btn').addEventListener('click', () => {
            this.pauseAllTasks();
        });

        // Data export
        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportManager.showExportDialog();
        });

        // Real-time updates
        this.wsManager.on('task_progress', (data) => {
            this.taskMonitor.updateProgress(data);
        });

        this.wsManager.on('scraping_complete', (data) => {
            this.handleScrapingComplete(data);
            this.dataViewer.refreshData();
        });
    }

    async startScrapingTask() {
        const config = this.getScrapingConfig();
        
        try {
            const response = await eel.start_scraping_task(config)();
            this.taskMonitor.addTask(response.task_id, config);
            this.showNotification('Scraping task started successfully', 'success');
        } catch (error) {
            this.showNotification(`Error starting task: ${error.message}`, 'error');
        }
    }

    getScrapingConfig() {
        const form = document.getElementById('scraping-config-form');
        const formData = new FormData(form);
        
        return {
            urls: formData.getAll('urls'),
            selectors: {
                title: formData.get('title-selector'),
                content: formData.get('content-selector'),
                links: formData.get('links-selector')
            },
            options: {
                delay: parseInt(formData.get('delay')) || 1000,
                max_pages: parseInt(formData.get('max-pages')) || 100,
                respect_robots: formData.get('respect-robots') === 'on',
                use_proxy: formData.get('use-proxy') === 'on'
            }
        };
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.getElementById('notifications').appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}
```

**Task Monitor Component (task-monitor.js)**
```javascript
class TaskMonitor {
    constructor() {
        this.tasks = new Map();
        this.container = document.getElementById('task-monitor');
    }

    addTask(taskId, config) {
        const task = {
            id: taskId,
            config: config,
            status: 'starting',
            progress: 0,
            startTime: new Date(),
            pagesScraped: 0,
            errors: 0
        };

        this.tasks.set(taskId, task);
        this.renderTask(task);
    }

    updateProgress(data) {
        const task = this.tasks.get(data.task_id);
        if (!task) return;

        Object.assign(task, {
            status: data.status,
            progress: data.progress,
            pagesScraped: data.pages_scraped,
            errors: data.errors,
            currentUrl: data.current_url
        });

        this.updateTaskDisplay(task);
    }

    renderTask(task) {
        const taskElement = document.createElement('div');
        taskElement.className = 'task-card';
        taskElement.id = `task-${task.id}`;
        
        taskElement.innerHTML = `
            <div class="task-header">
                <h3>Task ${task.id}</h3>
                <div class="task-controls">
                    <button onclick="taskMonitor.pauseTask('${task.id}')" class="btn-pause">Pause</button>
                    <button onclick="taskMonitor.stopTask('${task.id}')" class="btn-stop">Stop</button>
                </div>
            </div>
            <div class="task-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${task.progress}%"></div>
                </div>
                <span class="progress-text">${task.progress}%</span>
            </div>
            <div class="task-stats">
                <div class="stat">
                    <label>Status:</label>
                    <span class="status status-${task.status}">${task.status}</span>
                </div>
                <div class="stat">
                    <label>Pages:</label>
                    <span>${task.pagesScraped}</span>
                </div>
                <div class="stat">
                    <label>Errors:</label>
                    <span class="error-count">${task.errors}</span>
                </div>
                <div class="stat">
                    <label>Current:</label>
                    <span class="current-url" title="${task.currentUrl || 'N/A'}">${this.truncateUrl(task.currentUrl)}</span>
                </div>
            </div>
        `;

        this.container.appendChild(taskElement);
    }

    updateTaskDisplay(task) {
        const element = document.getElementById(`task-${task.id}`);
        if (!element) return;

        element.querySelector('.progress-fill').style.width = `${task.progress}%`;
        element.querySelector('.progress-text').textContent = `${task.progress}%`;
        element.querySelector('.status').className = `status status-${task.status}`;
        element.querySelector('.status').textContent = task.status;
        element.querySelector('.stat:nth-child(2) span').textContent = task.pagesScraped;
        element.querySelector('.error-count').textContent = task.errors;
        
        const currentUrlSpan = element.querySelector('.current-url');
        currentUrlSpan.textContent = this.truncateUrl(task.currentUrl);
        currentUrlSpan.title = task.currentUrl || 'N/A';
    }

    async pauseTask(taskId) {
        try {
            await eel.pause_task(taskId)();
            this.showTaskMessage(taskId, 'Task paused', 'info');
        } catch (error) {
            this.showTaskMessage(taskId, `Error pausing task: ${error.message}`, 'error');
        }
    }

    async stopTask(taskId) {
        try {
            await eel.stop_task(taskId)();
            this.tasks.delete(taskId);
            document.getElementById(`task-${taskId}`).remove();
            this.showTaskMessage(taskId, 'Task stopped', 'info');
        } catch (error) {
            this.showTaskMessage(taskId, `Error stopping task: ${error.message}`, 'error');
        }
    }

    truncateUrl(url, maxLength = 50) {
        if (!url) return 'N/A';
        return url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
    }

    showTaskMessage(taskId, message, type) {
        // Implementation for task-specific notifications
        console.log(`Task ${taskId}: ${message}`);
    }
}
```

**Data Viewer Component (data-viewer.js)**
```javascript
class DataViewer {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 50;
        this.filters = {};
        this.sortBy = 'created_at';
        this.sortOrder = 'desc';
        this.init();
    }

    init() {
        this.setupPagination();
        this.setupFilters();
        this.setupSorting();
        this.loadData();
    }

    async loadData() {
        try {
            const params = {
                page: this.currentPage,
                page_size: this.pageSize,
                filters: this.filters,
                sort_by: this.sortBy,
                sort_order: this.sortOrder
            };

            const response = await eel.get_scraped_data(params)();
            this.renderData(response.data);
            this.updatePagination(response.pagination);
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load scraped data');
        }
    }

    renderData(data) {
        const tbody = document.querySelector('#data-table tbody');
        tbody.innerHTML = '';

        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <input type="checkbox" value="${item.id}" class="row-select">
                </td>
                <td>${item.id}</td>
                <td>
                    <a href="${item.url}" target="_blank" class="url-link">
                        ${this.truncateText(item.url, 50)}
                    </a>
                </td>
                <td>${this.truncateText(item.title, 60)}</td>
                <td>${this.formatDate(item.created_at)}</td>
                <td>
                    <span class="status-badge status-${item.status}">${item.status}</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button onclick="dataViewer.viewItem(${item.id})" class="btn-view">View</button>
                        <button onclick="dataViewer.editItem(${item.id})" class="btn-edit">Edit</button>
                        <button onclick="dataViewer.deleteItem(${item.id})" class="btn-delete">Delete</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        this.setupRowSelection();
    }

    setupFilters() {
        const filterForm = document.getElementById('data-filters');
        filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        // Real-time search
        const searchInput = document.getElementById('search-input');
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.filters.search = e.target.value;
                this.currentPage = 1;
                this.loadData();
            }, 500);
        });
    }

    applyFilters() {
        const form = document.getElementById('data-filters');
        const formData = new FormData(form);
        
        this.filters = {
            search: formData.get('search') || '',
            status: formData.get('status') || '',
            date_from: formData.get('date_from') || '',
            date_to: formData.get('date_to') || '',
            domain: formData.get('domain') || ''
        };

        this.currentPage = 1;
        this.loadData();
    }

    setupSorting() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => {
                const field = header.dataset.field;
                
                if (this.sortBy === field) {
                    this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortBy = field;
                    this.sortOrder = 'asc';
                }

                this.updateSortingUI();
                this.loadData();
            });
        });
    }

    updateSortingUI() {
        document.querySelectorAll('.sortable').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
            if (header.dataset.field === this.sortBy) {
                header.classList.add(`sort-${this.sortOrder}`);
            }
        });
    }

    async viewItem(itemId) {
        try {
            const item = await eel.get_scraped_item(itemId)();
            this.showItemModal(item);
        } catch (error) {
            this.showError(`Error loading item: ${error.message}`);
        }
    }

    showItemModal(item) {
        const modal = document.getElementById('item-modal');
        const content = modal.querySelector('.modal-content');
        
        content.innerHTML = `
            <div class="modal-header">
                <h2>Scraped Item Details</h2>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="item-details">
                    <div class="detail-group">
                        <label>ID:</label>
                        <span>${item.id}</span>
                    </div>
                    <div class="detail-group">
                        <label>URL:</label>
                        <a href="${item.url}" target="_blank">${item.url}</a>
                    </div>
                    <div class="detail-group">
                        <label>Title:</label>
                        <span>${item.title}</span>
                    </div>
                    <div class="detail-group">
                        <label>Content:</label>
                        <div class="content-preview">${item.content}</div>
                    </div>
                    <div class="detail-group">
                        <label>Metadata:</label>
                        <pre class="metadata-json">${JSON.stringify(item.metadata, null, 2)}</pre>
                    </div>
                    <div class="detail-group">
                        <label>Created:</label>
                        <span>${this.formatDate(item.created_at)}</span>
                    </div>
                </div>
            </div>
        `;

        modal.style.display = 'block';
        
        // Close modal handlers
        modal.querySelector('.modal-close').onclick = () => {
            modal.style.display = 'none';
        };
        
        window.onclick = (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    }

    truncateText(text, maxLength) {
        if (!text) return 'N/A';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleString();
    }

    setupRowSelection() {
        const selectAll = document.getElementById('select-all');
        const rowSelects = document.querySelectorAll('.row-select');

        selectAll.addEventListener('change', (e) => {
            rowSelects.forEach(checkbox => {
                checkbox.checked = e.target.checked;
            });
            this.updateBulkActions();
        });

        rowSelects.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActions();
            });
        });
    }

    updateBulkActions() {
        const selected = document.querySelectorAll('.row-select:checked');
        const bulkActions = document.getElementById('bulk-actions');
        
        if (selected.length > 0) {
            bulkActions.style.display = 'block';
            bulkActions.querySelector('.selected-count').textContent = selected.length;
        } else {
            bulkActions.style.display = 'none';
        }
    }
}
```

#### 3.3 WebSocket Manager for Real-time Updates

**WebSocket Manager (websocket-manager.js)**
```javascript
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.listeners = {};
        this.connect();
    }

    connect() {
        try {
            this.ws = new WebSocket(`ws://localhost:8080/ws`);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.emit(data.type, data.payload);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.emit('disconnected');
                this.handleReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };

        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.handleReconnect();
        }
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            this.emit('max_reconnect_attempts_reached');
        }
    }

    send(type, payload) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, payload }));
        } else {
            console.warn('WebSocket not connected. Message not sent:', { type, payload });
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}
```

#### 3.4 Enhanced Python Backend for Frontend Integration

**Frontend Controller (frontend_controller.py)**
```python
import eel
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import websockets
import threading

from core.scraper_engine import ScraperEngine
from core.data_manager import DataManager
from core.config_manager import ConfigManager

class FrontendController:
    def __init__(self):
        self.scraper_engine = ScraperEngine()
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        self.active_tasks = {}
        self.websocket_clients = set()
        
    def initialize_eel(self):
        """Initialize Eel with web directory"""
        eel.init('web')
        
        # Expose Python functions to JavaScript
        eel.expose(self.start_scraping_task)
        eel.expose(self.get_scraped_data)
        eel.expose(self.get_scraped_item)
        eel.expose(self.pause_task)
        eel.expose(self.stop_task)
        eel.expose(self.get_task_status)
        eel.expose(self.export_data)
        eel.expose(self.get_system_stats)
        
        # Start WebSocket server in separate thread
        websocket_thread = threading.Thread(target=self.start_websocket_server)
        websocket_thread.daemon = True
        websocket_thread.start()
        
    async def start_scraping_task(self, config: Dict) -> Dict:
        """Start a new scraping task"""
        try:
            # Validate configuration
            self.validate_scraping_config(config)
            
            # Create task
            task_id = await self.scraper_engine.create_task(config)
            
            # Store task reference
            self.active_tasks[task_id] = {
                'config': config,
                'status': 'starting',
                'created_at': datetime.now().isoformat()
            }
            
            # Start task with progress callback
            await self.scraper_engine.start_task(
                task_id, 
                progress_callback=self.task_progress_callback
            )
            
            return {
                'success': True,
                'task_id': task_id,
                'message': 'Scraping task started successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to start scraping task: {str(e)}'
            }
    
    def validate_scraping_config(self, config: Dict):
        """Validate scraping configuration"""
        required_fields = ['urls', 'selectors']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        if not config['urls']:
            raise ValueError("At least one URL is required")
        
        if not config['selectors']:
            raise ValueError("At least one selector is required")
    
    async def task_progress_callback(self, task_id: str, progress_data: Dict):
        """Callback for task progress updates"""
        # Update local task status
        if task_id in self.active_tasks:
            self.active_tasks[task_id].update(progress_data)
        
        # Broadcast to WebSocket clients
        await self.broadcast_websocket({
            'type': 'task_progress',
            'payload': {
                'task_id': task_id,
                **progress_data
            }
        })
    
    async def get_scraped_data(self, params: Dict) -> Dict:
        """Get paginated scraped data with filters"""
        try:
            page = params.get('page', 1)
            page_size = params.get('page_size', 50)
            filters = params.get('filters', {})
            sort_by = params.get('sort_by', 'created_at')
            sort_order = params.get('sort_order', 'desc')
            
            # Get data from database
            result = await self.data_manager.get_scraped_data(
                page=page,
                page_size=page_size,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            return {
                'success': True,
                'data': result['data'],
                'pagination': {
                    'current_page': page,
                    'total_pages': result['total_pages'],
                    'total_items': result['total_items'],
                    'page_size': page_size
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to get scraped data: {str(e)}'
            }
    
    async def get_scraped_item(self, item_id: int) -> Dict:
        """Get single scraped item by ID"""
        try:
            item = await self.data_manager.get_item_by_id(item_id)
            if not item:
                raise ValueError(f"Item with ID {item_id} not found")
            
            return {
                'success': True,
                'data': item
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to get item: {str(e)}'
            }
    
    async def pause_task(self, task_id: str) -> Dict:
        """Pause a running task"""
        try:
            await self.scraper_engine.pause_task(task_id)
            
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['status'] = 'paused'
            
            await self.broadcast_websocket({
                'type': 'task_paused',
                'payload': {'task_id': task_id}
            })
            
            return {
                'success': True,
                'message': 'Task paused successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to pause task: {str(e)}'
            }
    
    async def stop_task(self, task_id: str) -> Dict:
        """Stop a running task"""
        try:
            await self.scraper_engine.stop_task(task_id)
            
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            await self.broadcast_websocket({
                'type': 'task_stopped',
                'payload': {'task_id': task_id}
            })
            
            return {
                'success': True,
                'message': 'Task stopped successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to stop task: {str(e)}'
            }
    
    async def export_data(self, export_config: Dict) -> Dict:
        """Export scraped data"""
        try:
            format_type = export_config.get('format', 'csv')
            filters = export_config.get('filters', {})
            
            file_path = await self.data_manager.export_data(
                format_type=format_type,
                filters=filters
            )
            
            return {
                'success': True,
                'file_path': file_path,
                'message': f'Data exported successfully to {file_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to export data: {str(e)}'
            }
    
    async def get_system_stats(self) -> Dict:
        """Get system statistics"""
        try:
            stats = {
                'active_tasks': len(self.active_tasks),
                'total_items_scraped': await self.data_manager.get_total_items_count(),
                'disk_usage': await self.get_disk_usage(),
                'memory_usage': await self.get_memory_usage(),
                'uptime': await self.get_uptime()
            }
            
            return {
                'success': True,
                'data': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to get system stats: {str(e)}'
            }
    
    def start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        async def handle_client(websocket, path):
            self.websocket_clients.add(websocket)
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_clients.remove(websocket)
        
        start_server = websockets.serve(handle_client, "localhost", 8080)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server)
        loop.run_forever()
    
    async def broadcast_websocket(self, message: Dict):
        """Broadcast message to all WebSocket clients"""
        if self.websocket_clients:
            message_str = json.dumps(message)
            await asyncio.gather(
                *[client.send(message_str) for client in self.websocket_clients],
                return_exceptions=True
            )
    
    def start_frontend(self, debug=True):
        """Start the Eel frontend"""
        try:
            eel.start('index.html', size=(1200, 800), mode='chrome', debug=debug)
        except (SystemExit, MemoryError, KeyboardInterrupt):
            print("Shutting down frontend...")
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        # Stop all active tasks
        for task_id in list(self.active_tasks.keys()):
            asyncio.run(self.stop_task(task_id))
        
        # Close WebSocket connections
        for client in self.websocket_clients:
            asyncio.run(client.close())
```

#### 3.5 Responsive CSS Framework

**Main Styles (main.css)**
```css
/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary-color: #3498db;
    --secondary-color: #2c3e50;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --error-color: #e74c3c;
    --background-color: #ecf0f1;
    --card-background: #ffffff;
    --text-primary: #2c3e50;
    --text-secondary: #7f8c8d;
    --border-color: #bdc3c7;
    --shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    --border-radius: 8px;
    --transition: all 0.3s ease;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.6;
}

/* Layout Components */
.app-container {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 250px;
    background-color: var(--secondary-color);
    color: white;
    padding: 20px;
    box-shadow: var(--shadow);
}

.main-content {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
}

.header {
    background-color: var(--card-background);
    padding: 15px 20px;
    margin-bottom: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Card Components */
.card {
    background-color: var(--card-background);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: 20px;
    margin-bottom: 20px;
    transition: var(--transition);
}

.card:hover {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-color);
}

.card-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
}

/* Form Components */
.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: var(--text-primary);
}

.form-input {
    width: 100%;
    padding: 10px 15px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 14px;
    transition: var(--transition);
}

.form-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-select {
    width: 100%;
    padding: 10px 15px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background-color: white;
    cursor: pointer;
}

/* Button Components */
.btn {
    padding: 10px 20px;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: var(--transition);
    text-decoration: none;
    display: inline-block;
    text-align: center;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background-color: #2980b9;
    transform: translateY(-1px);
}

.btn-success {
    background-color: var(--success-color);
    color: white;
}

.btn-warning {
    background-color: var(--warning-color);
    color: white;
}

.btn-error {
    background-color: var(--error-color);
    color: white;
}

.btn-secondary {
    background-color: var(--text-secondary);
    color: white;
}

/* Progress Components */
.progress-bar {
    width: 100%;
    height: 20px;
    background-color: #ecf0f1;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-color), #5dade2);
    transition: width 0.3s ease;
    position: relative;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
        45deg,
        transparent 35%,
        rgba(255, 255, 255, 0.2) 35%,
        rgba(255, 255, 255, 0.2) 65%,
        transparent 65%
    );
    background-size: 20px 20px;
    animation: move 1s linear infinite;
}

@keyframes move {
    0% { background-position: 0 0; }
    100% { background-position: 20px 20px; }
}

/* Task Monitor Styles */
.task-card {
    border-left: 4px solid var(--primary-color);
    margin-bottom: 15px;
    background-color: var(--card-background);
    border-radius: var(--border-radius);
    padding: 15px;
    box-shadow: var(--shadow);
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.task-header h3 {
    color: var(--text-primary);
    font-size: 1.1rem;
}

.task-controls {
    display: flex;
    gap: 10px;
}

.task-controls button {
    padding: 5px 12px;
    font-size: 12px;
    border-radius: 4px;
}

.task-progress {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.task-progress .progress-bar {
    flex: 1;
    height: 8px;
}

.progress-text {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
    min-width: 40px;
}

.task-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px;
}

.stat {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.stat label {
    font-size: 11px;
    color: var(--text-secondary);
    text-transform: uppercase;
    font-weight: 600;
}

.stat span {
    font-size: 13px;
    color: var(--text-primary);
}

/* Status Badges */
.status {
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.status-running {
    background-color: var(--success-color);
    color: white;
}

.status-paused {
    background-color: var(--warning-color);
    color: white;
}

.status-completed {
    background-color: var(--primary-color);
    color: white;
}

.status-error {
    background-color: var(--error-color);
    color: white;
}

.status-starting {
    background-color: var(--text-secondary);
    color: white;
}

/* Table Styles */
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background-color: var(--card-background);
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow);
}

.data-table th,
.data-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.data-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: var(--text-primary);
    cursor: pointer;
    user-select: none;
    position: relative;
}

.data-table th.sortable:hover {
    background-color: #e9ecef;
}

.data-table th.sort-asc::after,
.data-table th.sort-desc::after {
    content: '';
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
}

.data-table th.sort-asc::after {
    border-bottom: 6px solid var(--text-secondary);
}

.data-table th.sort-desc::after {
    border-top: 6px solid var(--text-secondary);
}

.data-table tr:hover {
    background-color: #f8f9fa;
}

.url-link {
    color: var(--primary-color);
    text-decoration: none;
}

.url-link:hover {
    text-decoration: underline;
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
    background-color: var(--card-background);
    margin: 5% auto;
    padding: 0;
    border-radius: var(--border-radius);
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
    padding: 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--text-secondary);
}

.modal-body {
    padding: 20px;
}

/* Notification Styles */
.notification {
    padding: 15px 20px;
    margin: 10px 0;
    border-radius: var(--border-radius);
    position: relative;
    animation: slideIn 0.3s ease;
}

.notification-success {
    background-color: #d4edda;
    border-left: 4px solid var(--success-color);
    color: #155724;
}

.notification-error {
    background-color: #f8d7da;
    border-left: 4px solid var(--error-color);
    color: #721c24;
}

.notification-warning {
    background-color: #fff3cd;
    border-left: 4px solid var(--warning-color);
    color: #856404;
}

.notification-info {
    background-color: #d1ecf1;
    border-left: 4px solid var(--primary-color);
    color: #0c5460;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .app-container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        padding: 15px;
    }
    
    .main-content {
        padding: 15px;
    }
    
    .header {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }
    
    .task-stats {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .data-table {
        font-size: 12px;
    }
    
    .data-table th,
    .data-table td {
        padding: 8px 10px;
    }
    
    .modal-content {
        width: 95%;
        margin: 10% auto;
    }
}

@media (max-width: 480px) {
    .task-stats {
        grid-template-columns: 1fr;
    }
    
    .task-controls {
        flex-direction: column;
        gap: 5px;
    }
    
    .btn {
        width: 100%;
        text-align: center;
    }
}

/* Dark Theme */
@media (prefers-color-scheme: dark) {
    :root {
        --background-color: #2c3e50;
        --card-background: #34495e;
        --text-primary: #ecf0f1;
        --text-secondary: #bdc3c7;
        --border-color: #7f8c8d;
    }
    
    .data-table th {
        background-color: #3a4f5c;
    }
    
    .form-input,
    .form-select {
        background-color: var(--card-background);
        color: var(--text-primary);
        border-color: var(--border-color);
    }
}
```

### 3.6 Validation & Success Criteria

**Frontend Validation Script (validate_frontend.py)**
```python
#!/usr/bin/env python3

import sys
import os
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class FrontendValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            sys.exit(1)
    
    def validate_page_load(self):
        """Test that main page loads correctly"""
        print("🔍 Testing page load...")
        
        try:
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "app-container"))
            )
            print("✅ Main page loads successfully")
            return True
        except Exception as e:
            print(f"❌ Page load failed: {e}")
            return False
    
    def validate_components(self):
        """Test that key components are present"""
        print("🔍 Testing component presence...")
        
        components = [
            ("sidebar", ".sidebar"),
            ("dashboard", "#scraper-dashboard"),
            ("task-monitor", "#task-monitor"),
            ("data-viewer", "#data-viewer"),
            ("scraping-form", "#scraping-config-form")
        ]
        
        results = []
        for name, selector in components:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    print(f"✅ {name} component found and visible")
                    results.append(True)
                else:
                    print(f"❌ {name} component found but not visible")
                    results.append(False)
            except Exception as e:
                print(f"❌ {name} component not found: {e}")
                results.append(False)
        
        return all(results)
    
    def validate_form_functionality(self):
        """Test form interactions"""
        print("🔍 Testing form functionality...")
        
        try:
            # Fill out scraping form
            url_input = self.driver.find_element(By.NAME, "urls")
            url_input.clear()
            url_input.send_keys("https://example.com")
            
            title_selector = self.driver.find_element(By.NAME, "title-selector")
            title_selector.clear()
            title_selector.send_keys("h1")
            
            # Check form validation
            form = self.driver.find_element(By.ID, "scraping-config-form")
            if form:
                print("✅ Form elements interactive")
                return True
            
        except Exception as e:
            print(f"❌ Form functionality failed: {e}")
            return False
    
    def validate_responsive_design(self):
        """Test responsive design"""
        print("🔍 Testing responsive design...")
        
        viewports = [
            (1920, 1080, "Desktop"),
            (768, 1024, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        results = []
        for width, height, device in viewports:
            try:
                self.driver.set_window_size(width, height)
                time.sleep(1)  # Allow layout to adjust
                
                # Check if sidebar is properly handled
                sidebar = self.driver.find_element(By.CLASS_NAME, "sidebar")
                main_content = self.driver.find_element(By.CLASS_NAME, "main-content")
                
                if sidebar and main_content:
                    print(f"✅ {device} layout working")
                    results.append(True)
                else:
                    print(f"❌ {device} layout broken")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ {device} responsive test failed: {e}")
                results.append(False)
        
        return all(results)
    
    def validate_websocket_connection(self):
        """Test WebSocket functionality"""
        print("🔍 Testing WebSocket connection...")
        
        try:
            # Execute JavaScript to test WebSocket
            ws_test = """
            return new Promise((resolve) => {
                const ws = new WebSocket('ws://localhost:8080/ws');
                ws.onopen = () => {
                    ws.close();
                    resolve(true);
                };
                ws.onerror = () => resolve(false);
                setTimeout(() => resolve(false), 5000);
            });
            """
            
            result = self.driver.execute_async_script(ws_test)
            if result:
                print("✅ WebSocket connection successful")
                return True
            else:
                print("❌ WebSocket connection failed")
                return False
                
        except Exception as e:
            print(f"❌ WebSocket test error: {e}")
            return False
    
    def run_validation(self):
        """Run all validation tests"""
        print("🚀 Starting Frontend Validation Tests")
        print("=" * 50)
        
        tests = [
            ("Page Load", self.validate_page_load),
            ("Components", self.validate_components),
            ("Form Functionality", self.validate_form_functionality),
            ("Responsive Design", self.validate_responsive_design),
            ("WebSocket Connection", self.validate_websocket_connection)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} test...")
            results[test_name] = test_func()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All frontend validation tests passed!")
            return True
        else:
            print("❌ Some frontend validation tests failed!")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    validator = FrontendValidator()
    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
    finally:
        validator.cleanup()
```

### 3.7 Troubleshooting Guide

**Common Frontend Issues and Solutions:**

1. **Eel Connection Issues**
   - Ensure Python backend is running before starting frontend
   - Check firewall settings for local ports
   - Verify Chrome/Chromium installation

2. **WebSocket Connection Failures**
   - Confirm WebSocket server is running on correct port
   - Check browser developer console for connection errors
   - Validate WebSocket URL in JavaScript code

3. **Component Not Loading**
   - Verify JavaScript module imports
   - Check browser console for syntax errors
   - Ensure all dependencies are loaded

4. **Real-time Updates Not Working**
   - Confirm WebSocket connection is established
   - Check Python callback functions are called
   - Verify message format matches expected structure

5. **Performance Issues**
   - Optimize large data rendering with pagination
   - Implement virtual scrolling for long lists
   - Use CSS transforms for animations instead of changing layout properties

### Success Criteria
- [ ] All UI components render correctly
- [ ] Real-time progress updates function properly
- [ ] Data visualization displays scraped content
- [ ] Export functionality works for all formats
- [ ] Responsive design works on all target devices
- [ ] WebSocket connections maintain stability
- [ ] Form validation prevents invalid submissions
- [ ] Error handling provides meaningful feedback
- [ ] Performance remains smooth with large datasets
- [ ] All validation tests pass

This completes Phase 3 with a comprehensive frontend implementation that provides a modern, responsive, and feature-rich interface for the ScraperV4 system.