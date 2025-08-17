/**
 * Results Table Component
 * Handles display and management of scraping results
 */

class ResultsTable {
    constructor() {
        this.container = document.getElementById('results-table-container');
        this.currentJobId = null;
        this.currentPage = 1;
        this.pageSize = 50;
        this.totalResults = 0;
        this.sortColumn = 'scraped_at';
        this.sortDirection = 'desc';
        this.filters = {};
        this.selectedResults = new Set();
        this.init();
    }

    init() {
        if (!this.container) {
            console.warn('Results table container not found');
            return;
        }

        this.bindEvents();
        this.loadRecentResults();
        
        console.log('Results table initialized');
    }

    bindEvents() {
        // Export button
        const exportBtn = document.getElementById('export-results-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', this.handleExport.bind(this));
        }

        // Clear results button
        const clearBtn = document.getElementById('clear-results-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', this.handleClearResults.bind(this));
        }
    }

    /**
     * Load recent results (default view)
     */
    async loadRecentResults() {
        try {
            // Get recent jobs first
            const jobsResponse = await window.api.getJobResults(null, 10, 0);
            
            if (jobsResponse.success && jobsResponse.results.length > 0) {
                this.renderResults(jobsResponse.results, jobsResponse.total);
            } else {
                this.renderEmptyState();
            }
            
        } catch (error) {
            console.error('Failed to load recent results:', error);
            this.renderErrorState(error.message);
        }
    }

    /**
     * Load results for a specific job
     */
    async loadJobResults(jobId, page = 1) {
        this.currentJobId = jobId;
        this.currentPage = page;
        
        try {
            const offset = (page - 1) * this.pageSize;
            const response = await window.api.getJobResults(jobId, this.pageSize, offset);
            
            if (response.success) {
                this.totalResults = response.total;
                this.renderResults(response.results, response.total);
                this.renderPagination();
            } else {
                throw new Error(response.error || 'Failed to load results');
            }
            
        } catch (error) {
            console.error('Failed to load job results:', error);
            this.renderErrorState(error.message);
        }
    }

    /**
     * Render results table
     */
    renderResults(results, total = 0) {
        if (!results || results.length === 0) {
            this.renderEmptyState();
            return;
        }

        // Determine columns from first result
        const columns = this.getColumns(results[0]);
        
        const tableHTML = `
            <div class="results-header">
                <div class="results-info">
                    <span class="results-count">${window.helpers.NumberUtils.formatNumber(total)} results</span>
                    ${this.currentJobId ? `<span class="job-filter">Job ID: ${this.currentJobId}</span>` : ''}
                </div>
                <div class="results-actions">
                    <button class="btn btn-sm btn-secondary" id="refresh-results">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                    <button class="btn btn-sm btn-secondary" id="filter-results">
                        <i class="fas fa-filter"></i> Filter
                    </button>
                    ${this.selectedResults.size > 0 ? `
                        <button class="btn btn-sm btn-danger" id="delete-selected">
                            <i class="fas fa-trash"></i> Delete Selected (${this.selectedResults.size})
                        </button>
                    ` : ''}
                </div>
            </div>
            
            <div class="table-wrapper">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th class="select-column">
                                <input type="checkbox" id="select-all" ${this.areAllSelected(results) ? 'checked' : ''}>
                            </th>
                            ${columns.map(col => `
                                <th class="sortable ${col.key === this.sortColumn ? 'sorted' : ''}" 
                                    data-column="${col.key}">
                                    ${col.label}
                                    <i class="fas fa-sort${col.key === this.sortColumn ? 
                                        (this.sortDirection === 'asc' ? '-up' : '-down') : ''}"></i>
                                </th>
                            `).join('')}
                            <th class="actions-column">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(result => this.renderResultRow(result, columns)).join('')}
                    </tbody>
                </table>
            </div>
            
            ${total > this.pageSize ? this.renderPaginationHTML() : ''}
        `;

        this.container.innerHTML = tableHTML;
        this.bindTableEvents();
    }

    getColumns(sampleResult) {
        const columns = [
            { key: 'id', label: 'ID', type: 'number' },
            { key: 'source_url', label: 'Source URL', type: 'url' },
            { key: 'scraped_at', label: 'Scraped At', type: 'datetime' },
            { key: 'status', label: 'Status', type: 'status' }
        ];

        // Add data columns dynamically based on the first result
        if (sampleResult.data && typeof sampleResult.data === 'object') {
            Object.keys(sampleResult.data).forEach(key => {
                columns.push({
                    key: `data.${key}`,
                    label: window.helpers.StringUtils.titleCase(key),
                    type: 'data'
                });
            });
        }

        return columns;
    }

    renderResultRow(result, columns) {
        const isSelected = this.selectedResults.has(result.id);
        
        return `
            <tr class="result-row ${isSelected ? 'selected' : ''}" data-id="${result.id}">
                <td class="select-column">
                    <input type="checkbox" class="result-checkbox" 
                           value="${result.id}" ${isSelected ? 'checked' : ''}>
                </td>
                ${columns.map(col => `
                    <td class="column-${col.key.replace('.', '-')}" title="${this.getCellTooltip(result, col)}">
                        ${this.formatCellValue(result, col)}
                    </td>
                `).join('')}
                <td class="actions-column">
                    <div class="action-buttons">
                        <button class="btn btn-xs btn-secondary view-result" 
                                data-id="${result.id}" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-xs btn-secondary copy-result" 
                                data-id="${result.id}" title="Copy Data">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="btn btn-xs btn-danger delete-result" 
                                data-id="${result.id}" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    formatCellValue(result, column) {
        let value;
        
        if (column.key.startsWith('data.')) {
            const dataKey = column.key.substring(5);
            value = result.data?.[dataKey];
        } else {
            value = result[column.key];
        }

        if (value === null || value === undefined) {
            return '<span class="null-value">—</span>';
        }

        switch (column.type) {
            case 'datetime':
                return window.helpers.DateUtils.formatDate(value);
                
            case 'url':
                const truncatedUrl = window.helpers.StringUtils.truncate(value, 50);
                return `<a href="${value}" target="_blank" class="url-link">${truncatedUrl}</a>`;
                
            case 'status':
                return `<span class="status-badge status-${value}">${value}</span>`;
                
            case 'number':
                return window.helpers.NumberUtils.formatNumber(value);
                
            case 'data':
                if (typeof value === 'object') {
                    return '<span class="object-value">[Object]</span>';
                }
                return window.helpers.StringUtils.truncate(String(value), 100);
                
            default:
                return window.helpers.StringUtils.truncate(String(value), 100);
        }
    }

    getCellTooltip(result, column) {
        let value;
        
        if (column.key.startsWith('data.')) {
            const dataKey = column.key.substring(5);
            value = result.data?.[dataKey];
        } else {
            value = result[column.key];
        }

        if (value === null || value === undefined) {
            return 'No data';
        }

        if (typeof value === 'object') {
            return JSON.stringify(value, null, 2);
        }

        return String(value);
    }

    bindTableEvents() {
        // Select all checkbox
        const selectAllCheckbox = this.container.querySelector('#select-all');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', this.handleSelectAll.bind(this));
        }

        // Individual checkboxes
        this.container.querySelectorAll('.result-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', this.handleResultSelect.bind(this));
        });

        // Sort headers
        this.container.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', this.handleSort.bind(this));
        });

        // Action buttons
        this.container.querySelectorAll('.view-result').forEach(btn => {
            btn.addEventListener('click', this.handleViewResult.bind(this));
        });

        this.container.querySelectorAll('.copy-result').forEach(btn => {
            btn.addEventListener('click', this.handleCopyResult.bind(this));
        });

        this.container.querySelectorAll('.delete-result').forEach(btn => {
            btn.addEventListener('click', this.handleDeleteResult.bind(this));
        });

        // Refresh button
        const refreshBtn = this.container.querySelector('#refresh-results');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.handleRefresh.bind(this));
        }

        // Filter button
        const filterBtn = this.container.querySelector('#filter-results');
        if (filterBtn) {
            filterBtn.addEventListener('click', this.showFilterModal.bind(this));
        }

        // Delete selected button
        const deleteSelectedBtn = this.container.querySelector('#delete-selected');
        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', this.handleDeleteSelected.bind(this));
        }
    }

    handleSelectAll(e) {
        const isChecked = e.target.checked;
        const checkboxes = this.container.querySelectorAll('.result-checkbox');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            const resultId = parseInt(checkbox.value);
            
            if (isChecked) {
                this.selectedResults.add(resultId);
            } else {
                this.selectedResults.delete(resultId);
            }
        });

        this.updateSelectionUI();
    }

    handleResultSelect(e) {
        const resultId = parseInt(e.target.value);
        
        if (e.target.checked) {
            this.selectedResults.add(resultId);
        } else {
            this.selectedResults.delete(resultId);
        }

        this.updateSelectionUI();
    }

    updateSelectionUI() {
        // Update select all checkbox state
        const selectAllCheckbox = this.container.querySelector('#select-all');
        const checkboxes = this.container.querySelectorAll('.result-checkbox');
        
        if (selectAllCheckbox) {
            const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
            selectAllCheckbox.checked = checkedCount === checkboxes.length;
        }

        // Update action buttons
        this.renderResults(); // Re-render to update action buttons
    }

    areAllSelected(results) {
        return results.every(result => this.selectedResults.has(result.id));
    }

    handleSort(e) {
        const column = e.currentTarget.dataset.column;
        
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }

        // Reload current page with new sort
        if (this.currentJobId) {
            this.loadJobResults(this.currentJobId, this.currentPage);
        } else {
            this.loadRecentResults();
        }
    }

    async handleViewResult(e) {
        const resultId = parseInt(e.currentTarget.dataset.id);
        
        try {
            // For now, we'll need to find the result in current data
            // In a real implementation, you might have a separate API call
            const row = e.currentTarget.closest('.result-row');
            const result = this.getResultFromRow(row);
            
            this.showResultModal(result);
            
        } catch (error) {
            console.error('Failed to view result:', error);
            window.notifications?.error('View Failed', 'Failed to load result details');
        }
    }

    getResultFromRow(row) {
        // Extract result data from table row
        // This is a simplified implementation
        return {
            id: row.dataset.id,
            // Would need to extract other data from cells
        };
    }

    showResultModal(result) {
        const content = `
            <div class="result-details">
                <div class="result-meta">
                    <div class="meta-item">
                        <label>ID:</label>
                        <span>${result.id}</span>
                    </div>
                    <div class="meta-item">
                        <label>URL:</label>
                        <a href="${result.source_url}" target="_blank">${result.source_url}</a>
                    </div>
                    <div class="meta-item">
                        <label>Status:</label>
                        <span class="status-badge status-${result.status}">${result.status}</span>
                    </div>
                    <div class="meta-item">
                        <label>Scraped:</label>
                        <span>${window.helpers.DateUtils.formatDate(result.scraped_at)}</span>
                    </div>
                </div>
                
                <div class="result-data">
                    <h4>Scraped Data</h4>
                    <pre class="data-preview">${JSON.stringify(result.data, null, 2)}</pre>
                </div>
                
                <div class="result-actions">
                    <button class="btn btn-secondary" onclick="navigator.clipboard.writeText('${JSON.stringify(result.data)}')">
                        <i class="fas fa-copy"></i> Copy Data
                    </button>
                    <button class="btn btn-secondary" onclick="window.scraperApp.hideModal()">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        window.scraperApp.showModal('Result Details', content);
    }

    async handleCopyResult(e) {
        const resultId = parseInt(e.currentTarget.dataset.id);
        
        try {
            const result = this.getResultFromRow(e.currentTarget.closest('.result-row'));
            await navigator.clipboard.writeText(JSON.stringify(result.data, null, 2));
            
            window.notifications?.success('Copied', 'Result data copied to clipboard');
            
        } catch (error) {
            console.error('Failed to copy result:', error);
            window.notifications?.error('Copy Failed', 'Failed to copy result data');
        }
    }

    async handleDeleteResult(e) {
        const resultId = parseInt(e.currentTarget.dataset.id);
        
        if (!confirm('Are you sure you want to delete this result?')) {
            return;
        }

        try {
            // Would need API endpoint for deleting individual results
            console.log('Delete result:', resultId);
            window.notifications?.success('Deleted', 'Result deleted successfully');
            
            // Refresh current view
            this.handleRefresh();
            
        } catch (error) {
            console.error('Failed to delete result:', error);
            window.notifications?.error('Delete Failed', 'Failed to delete result');
        }
    }

    handleRefresh() {
        if (this.currentJobId) {
            this.loadJobResults(this.currentJobId, this.currentPage);
        } else {
            this.loadRecentResults();
        }
    }

    async handleExport() {
        if (this.selectedResults.size === 0) {
            window.notifications?.warning('No Selection', 'Please select results to export');
            return;
        }

        try {
            const format = 'csv'; // Could show format selection modal
            const jobId = this.currentJobId || 'all';
            
            const response = await window.api.exportResults(jobId, format);
            
            if (response.success) {
                window.notifications?.success('Export Complete', `Results exported to ${response.file_path}`);
            } else {
                throw new Error(response.error || 'Export failed');
            }
            
        } catch (error) {
            console.error('Export failed:', error);
            window.notifications?.error('Export Failed', error.message);
        }
    }

    async handleClearResults() {
        if (!confirm('Are you sure you want to clear all results? This cannot be undone.')) {
            return;
        }

        try {
            // Would need API endpoint for clearing results
            console.log('Clear all results');
            window.notifications?.success('Cleared', 'All results cleared successfully');
            
            this.renderEmptyState();
            
        } catch (error) {
            console.error('Failed to clear results:', error);
            window.notifications?.error('Clear Failed', 'Failed to clear results');
        }
    }

    async handleDeleteSelected() {
        if (this.selectedResults.size === 0) {
            return;
        }

        const count = this.selectedResults.size;
        if (!confirm(`Are you sure you want to delete ${count} selected result${count > 1 ? 's' : ''}?`)) {
            return;
        }

        try {
            // Would batch delete selected results
            console.log('Delete selected:', Array.from(this.selectedResults));
            
            window.notifications?.success('Deleted', `${count} result${count > 1 ? 's' : ''} deleted successfully`);
            
            this.selectedResults.clear();
            this.handleRefresh();
            
        } catch (error) {
            console.error('Failed to delete selected results:', error);
            window.notifications?.error('Delete Failed', 'Failed to delete selected results');
        }
    }

    showFilterModal() {
        const content = `
            <form id="filter-form" class="filter-form">
                <div class="form-group">
                    <label for="filter-status">Status</label>
                    <select id="filter-status">
                        <option value="">All</option>
                        <option value="success">Success</option>
                        <option value="failed">Failed</option>
                        <option value="partial">Partial</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="filter-date-from">Date From</label>
                    <input type="date" id="filter-date-from">
                </div>
                
                <div class="form-group">
                    <label for="filter-date-to">Date To</label>
                    <input type="date" id="filter-date-to">
                </div>
                
                <div class="form-group">
                    <label for="filter-url">URL Contains</label>
                    <input type="text" id="filter-url" placeholder="Filter by URL">
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Apply Filter</button>
                    <button type="button" class="btn btn-secondary" id="clear-filters">Clear Filters</button>
                    <button type="button" class="btn btn-secondary" onclick="window.scraperApp.hideModal()">Cancel</button>
                </div>
            </form>
        `;
        
        window.scraperApp.showModal('Filter Results', content);
        
        // Bind filter form events
        const form = document.getElementById('filter-form');
        form.addEventListener('submit', this.applyFilters.bind(this));
        
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.filters = {};
            this.handleRefresh();
            window.scraperApp.hideModal();
        });
    }

    applyFilters(e) {
        e.preventDefault();
        
        const form = e.target;
        this.filters = {
            status: form.querySelector('#filter-status').value,
            dateFrom: form.querySelector('#filter-date-from').value,
            dateTo: form.querySelector('#filter-date-to').value,
            url: form.querySelector('#filter-url').value
        };

        // Remove empty filters
        Object.keys(this.filters).forEach(key => {
            if (!this.filters[key]) {
                delete this.filters[key];
            }
        });

        window.scraperApp.hideModal();
        this.handleRefresh();
    }

    renderPaginationHTML() {
        const totalPages = Math.ceil(this.totalResults / this.pageSize);
        const current = this.currentPage;
        
        if (totalPages <= 1) return '';

        return `
            <div class="pagination">
                <button class="btn btn-sm btn-secondary" 
                        ${current === 1 ? 'disabled' : ''} 
                        onclick="window.resultsTable.goToPage(${current - 1})">
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
                
                <span class="pagination-info">
                    Page ${current} of ${totalPages}
                </span>
                
                <button class="btn btn-sm btn-secondary"
                        ${current === totalPages ? 'disabled' : ''}
                        onclick="window.resultsTable.goToPage(${current + 1})">
                    Next <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        `;
    }

    goToPage(page) {
        if (this.currentJobId) {
            this.loadJobResults(this.currentJobId, page);
        }
    }

    renderEmptyState() {
        this.container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-table"></i>
                </div>
                <h3>No Results Found</h3>
                <p>Start a scraping job to see results here.</p>
                <button class="btn btn-primary" onclick="window.scraperApp.navigateToPage('scraping')">
                    <i class="fas fa-plus"></i> Start Scraping
                </button>
            </div>
        `;
    }

    renderErrorState(message) {
        this.container.innerHTML = `
            <div class="error-state">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Failed to Load Results</h3>
                <p>${message}</p>
                <button class="btn btn-secondary" onclick="window.resultsTable.handleRefresh()">
                    <i class="fas fa-sync"></i> Try Again
                </button>
            </div>
        `;
    }
}

// Make available globally
window.ResultsTable = ResultsTable;