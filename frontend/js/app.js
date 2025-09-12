// Employee Management System - Frontend JavaScript
// This handles all the frontend functionality and API communication

// Configuration
const API_BASE_URL = 'http://localhost:8000/employees';
let currentPage = 0;
let currentLimit = 20;
let allEmployees = [];
let filteredEmployees = [];

// DOM Elements
const sections = {
    dashboard: document.getElementById('dashboard-section'),
    employees: document.getElementById('employees-section'),
    addEmployee: document.getElementById('add-employee-section'),
    reports: document.getElementById('reports-section')
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Employee Management System loaded');
    initializeApp();
});

// Main initialization function
function initializeApp() {
    setupNavigation();
    setupEventListeners();
    loadDashboardData();
    loadEmployees();
    setupFormValidation();
}

// Navigation System
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            Object.values(sections).forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const sectionName = this.getAttribute('data-section');
            const section = document.getElementById(`${sectionName}-section`);
            if (section) {
                section.classList.add('active');
                
                // Load section-specific data
                switch(sectionName) {
                    case 'dashboard':
                        loadDashboardData();
                        break;
                    case 'employees':
                        loadEmployees();
                        break;
                    case 'reports':
                        loadReports();
                        break;
                }
            }
        });
    });
}

// Event Listeners Setup
function setupEventListeners() {
    // Employee form submission
    const employeeForm = document.getElementById('employee-form');
    if (employeeForm) {
        employeeForm.addEventListener('submit', handleEmployeeSubmit);
    }
    
    // Edit form submission
    const editForm = document.getElementById('edit-employee-form');
    if (editForm) {
        editForm.addEventListener('submit', handleEmployeeUpdate);
    }
    
    // Search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Set default joining date to today
    const joiningDateInput = document.getElementById('employee-joining-date');
    if (joiningDateInput) {
        joiningDateInput.value = new Date().toISOString().split('T')[0];
    }
}

// API Functions
async function apiRequest(url, options = {}) {
    showLoading();
    
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message || 'An error occurred', 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

// Dashboard Functions
async function loadDashboardData() {
    try {
        // Load employees for dashboard stats
        const data = await apiRequest(`${API_BASE_URL}/`);
        const employees = data.employees || [];
        
        // Calculate statistics
        updateDashboardStats(employees);
        
        // Load average salary statistics
        const avgSalaryData = await apiRequest(`${API_BASE_URL}/avg-salary/`);
        updateDepartmentStats(avgSalaryData || []);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Show default values on error
        updateDashboardStats([]);
        updateDepartmentStats([]);
    }
}

function updateDashboardStats(employees) {
    const totalEmployees = employees.length;
    const activeEmployees = employees.filter(emp => emp.is_active).length;
    const departments = [...new Set(employees.map(emp => emp.department))];
    const avgSalary = employees.length > 0 
        ? Math.round(employees.reduce((sum, emp) => sum + emp.salary, 0) / employees.length)
        : 0;
    
    // Update DOM elements
    document.getElementById('total-employees').textContent = totalEmployees;
    document.getElementById('total-departments').textContent = departments.length;
    document.getElementById('avg-salary').textContent = `$${avgSalary.toLocaleString()}`;
    document.getElementById('active-employees').textContent = activeEmployees;
}

function updateDepartmentStats(statistics) {
    const container = document.getElementById('department-stats');
    
    if (statistics.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No data available</p>';
        return;
    }
    
    container.innerHTML = statistics.map(stat => `
        <div class="dept-stat">
            <div class="dept-name">${stat.department}</div>
            <div class="dept-info">
                <span>Avg Salary: <strong>$${stat.avg_salary.toLocaleString()}</strong></span>
            </div>
        </div>
    `).join('');
}

// Employee Management Functions
async function loadEmployees(page = 0, limit = 20, filters = {}) {
    try {
        let url = `${API_BASE_URL}/?limit=${limit}&offset=${page * limit}`;
        
        // Add filters to URL
        if (filters.department) {
            url += `&department=${encodeURIComponent(filters.department)}`;
        }
        
        const data = await apiRequest(url);
        allEmployees = data.employees || [];
        
        // Apply client-side filters
        filteredEmployees = applyClientFilters(allEmployees, filters);
        
        updateEmployeesTable(filteredEmployees);
        updatePagination(data.pagination || {});
        updateDepartmentFilter();
        
    } catch (error) {
        console.error('Error loading employees:', error);
        updateEmployeesTable([]);
    }
}

function applyClientFilters(employees, filters) {
    let filtered = [...employees];
    
    // Search filter
    if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        filtered = filtered.filter(emp => 
            emp.name.toLowerCase().includes(searchTerm) ||
            emp.email.toLowerCase().includes(searchTerm) ||
            emp.employee_id.toLowerCase().includes(searchTerm) ||
            emp.department.toLowerCase().includes(searchTerm) ||
            emp.position.toLowerCase().includes(searchTerm)
        );
    }
    
    // Skill filter
    if (filters.skill) {
        const skillTerm = filters.skill.toLowerCase();
        filtered = filtered.filter(emp => 
            emp.skills && emp.skills.some(skill => 
                skill.toLowerCase().includes(skillTerm)
            )
        );
    }
    
    return filtered;
}

function updateEmployeesTable(employees) {
    const tbody = document.getElementById('employees-tbody');
    
    if (employees.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <i class="fas fa-users" style="font-size: 3rem; margin-bottom: 1rem; display: block;"></i>
                    No employees found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = employees.map(employee => `
        <tr>
            <td><strong>${escapeHtml(employee.employee_id)}</strong></td>
            <td>${escapeHtml(employee.name)}</td>
            <td>${escapeHtml(employee.email)}</td>
            <td>${escapeHtml(employee.department)}</td>
            <td>${escapeHtml(employee.position)}</td>
            <td>$${employee.salary.toLocaleString()}</td>
            <td>
                <div class="employee-skills">
                    ${(employee.skills || []).map(skill => 
                        `<span class="skill-tag">${escapeHtml(skill)}</span>`
                    ).join('')}
                </div>
            </td>
            <td>
                <span class="status-badge ${employee.is_active ? 'status-active' : 'status-inactive'}">
                    ${employee.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-sm btn-primary" onclick="editEmployee('${employee.employee_id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-error" onclick="deleteEmployee('${employee.employee_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function updateDepartmentFilter() {
    const select = document.getElementById('department-filter');
    const departments = [...new Set(allEmployees.map(emp => emp.department))].sort();
    
    // Preserve current selection
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">All Departments</option>' +
        departments.map(dept => `<option value="${dept}">${dept}</option>`).join('');
    
    // Restore selection
    select.value = currentValue;
}

function updatePagination(pagination) {
    const container = document.getElementById('pagination');
    
    if (!pagination.total || pagination.total <= pagination.limit) {
        container.innerHTML = '';
        return;
    }
    
    const totalPages = Math.ceil(pagination.total / pagination.limit);
    const currentPageNum = Math.floor(pagination.offset / pagination.limit);
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <button ${!pagination.has_previous ? 'disabled' : ''} 
                onclick="changePage(${currentPageNum - 1})">
            <i class="fas fa-chevron-left"></i> Previous
        </button>
    `;
    
    // Page numbers
    for (let i = 0; i < totalPages; i++) {
        if (i === currentPageNum) {
            paginationHTML += `<button class="active">${i + 1}</button>`;
        } else if (Math.abs(i - currentPageNum) <= 2 || i === 0 || i === totalPages - 1) {
            paginationHTML += `<button onclick="changePage(${i})">${i + 1}</button>`;
        } else if (Math.abs(i - currentPageNum) === 3) {
            paginationHTML += `<span>...</span>`;
        }
    }
    
    // Next button
    paginationHTML += `
        <button ${!pagination.has_next ? 'disabled' : ''} 
                onclick="changePage(${currentPageNum + 1})">
            Next <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    container.innerHTML = paginationHTML;
}

function changePage(page) {
    currentPage = page;
    const filters = getCurrentFilters();
    loadEmployees(page, currentLimit, filters);
}

// Form Handling
function setupFormValidation() {
    const form = document.getElementById('employee-form');
    const inputs = form.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Remove existing error styling
    field.classList.remove('error');
    
    // Validation rules
    switch(field.id) {
        case 'employee-id':
            if (!/^[A-Za-z0-9]{3,10}$/.test(value)) {
                showFieldError(field, 'Employee ID must be 3-10 alphanumeric characters');
            }
            break;
        case 'employee-email':
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                showFieldError(field, 'Please enter a valid email address');
            }
            break;
        case 'employee-salary':
            if (isNaN(value) || parseFloat(value) < 0) {
                showFieldError(field, 'Salary must be a positive number');
            }
            break;
    }
}

function showFieldError(field, message) {
    field.classList.add('error');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = 'var(--error-color)';
    errorDiv.style.fontSize = 'var(--font-size-sm)';
    errorDiv.style.marginTop = 'var(--spacing-xs)';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('error');
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

async function handleEmployeeSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const employeeData = {
        employee_id: document.getElementById('employee-id').value,
        name: document.getElementById('employee-name').value,
        email: document.getElementById('employee-email').value,
        department: document.getElementById('employee-department').value,
        position: document.getElementById('employee-position').value,
        salary: parseFloat(document.getElementById('employee-salary').value),
        skills: document.getElementById('employee-skills').value
            .split(',')
            .map(s => s.trim())
            .filter(s => s.length > 0),
        joining_date: document.getElementById('employee-joining-date').value,
        is_active: document.getElementById('employee-active').checked
    };
    
    try {
        await apiRequest(`${API_BASE_URL}/`, {
            method: 'POST',
            body: JSON.stringify(employeeData)
        });
        
        showToast('Employee created successfully!', 'success');
        clearForm();
        loadEmployees(); // Refresh the list
        loadDashboardData(); // Update dashboard
        
        // Switch to employees section
        document.querySelector('[data-section="employees"]').click();
        
    } catch (error) {
        console.error('Error creating employee:', error);
        showToast('Failed to create employee. Please check the data and try again.', 'error');
    }
}

async function handleEmployeeUpdate(event) {
    event.preventDefault();
    
    const employeeId = document.getElementById('edit-employee-id-hidden').value;
    const updateData = {
        name: document.getElementById('edit-employee-name').value,
        email: document.getElementById('edit-employee-email').value,
        department: document.getElementById('edit-employee-department').value,
        position: document.getElementById('edit-employee-position').value,
        salary: parseFloat(document.getElementById('edit-employee-salary').value),
        skills: document.getElementById('edit-employee-skills').value
            .split(',')
            .map(s => s.trim())
            .filter(s => s.length > 0),
        is_active: document.getElementById('edit-employee-active').checked
    };
    
    try {
        await apiRequest(`${API_BASE_URL}/${employeeId}/`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
        
        showToast('Employee updated successfully!', 'success');
        closeEditModal();
        loadEmployees(); // Refresh the list
        loadDashboardData(); // Update dashboard
        
    } catch (error) {
        console.error('Error updating employee:', error);
        showToast('Failed to update employee. Please try again.', 'error');
    }
}

// Employee Actions
async function editEmployee(employeeId) {
    try {
        const employee = await apiRequest(`${API_BASE_URL}/${employeeId}/`);
        
        // Populate edit form
        document.getElementById('edit-employee-id-hidden').value = employee.employee_id;
        document.getElementById('edit-employee-name').value = employee.name;
        document.getElementById('edit-employee-email').value = employee.email;
        document.getElementById('edit-employee-department').value = employee.department;
        document.getElementById('edit-employee-position').value = employee.position;
        document.getElementById('edit-employee-salary').value = employee.salary;
        document.getElementById('edit-employee-skills').value = (employee.skills || []).join(', ');
        document.getElementById('edit-employee-active').checked = employee.is_active;
        
        // Show modal
        document.getElementById('edit-modal').classList.add('show');
        
    } catch (error) {
        console.error('Error loading employee for edit:', error);
        showToast('Failed to load employee data', 'error');
    }
}

async function deleteEmployee(employeeId) {
    if (!confirm('Are you sure you want to delete this employee? This action cannot be undone.')) {
        return;
    }
    
    try {
        await apiRequest(`${API_BASE_URL}/${employeeId}/`, {
            method: 'DELETE'
        });
        
        showToast('Employee deleted successfully!', 'success');
        loadEmployees(); // Refresh the list
        loadDashboardData(); // Update dashboard
        
    } catch (error) {
        console.error('Error deleting employee:', error);
        showToast('Failed to delete employee. Please try again.', 'error');
    }
}

// Search and Filter Functions
function handleSearch(event) {
    const searchTerm = event.target.value.trim();
    const filters = getCurrentFilters();
    filters.search = searchTerm;
    
    // Apply filters to current data
    filteredEmployees = applyClientFilters(allEmployees, filters);
    updateEmployeesTable(filteredEmployees);
}

function searchEmployees() {
    const filters = getCurrentFilters();
    loadEmployees(0, currentLimit, filters);
}

function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('department-filter').value = '';
    document.getElementById('skill-filter').value = '';
    
    loadEmployees(0, currentLimit, {});
}

function getCurrentFilters() {
    return {
        search: document.getElementById('search-input').value.trim(),
        department: document.getElementById('department-filter').value,
        skill: document.getElementById('skill-filter').value.trim()
    };
}

// Utility Functions
function clearForm() {
    const form = document.getElementById('employee-form');
    form.reset();
    
    // Set default date
    document.getElementById('employee-joining-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('employee-active').checked = true;
    
    // Clear any error messages
    form.querySelectorAll('.field-error').forEach(error => error.remove());
    form.querySelectorAll('.error').forEach(field => field.classList.remove('error'));
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.remove('show');
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 
                type === 'error' ? 'fa-exclamation-circle' : 
                'fa-info-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
    
    // Allow manual dismissal
    toast.addEventListener('click', () => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Reports Functions
async function loadReports() {
    try {
        // Load department statistics
        const deptStats = await apiRequest(`${API_BASE_URL}/department-stats/`);
        updateDepartmentReport(deptStats.statistics || []);
        
        // Load employees for salary analysis
        const employeesData = await apiRequest(`${API_BASE_URL}/`);
        updateSalaryReport(employeesData.employees || []);
        
    } catch (error) {
        console.error('Error loading reports:', error);
        document.getElementById('department-report').innerHTML = 
            '<p style="text-align: center; color: var(--text-secondary);">Failed to load report data</p>';
        document.getElementById('salary-report').innerHTML = 
            '<p style="text-align: center; color: var(--text-secondary);">Failed to load report data</p>';
    }
}

function updateDepartmentReport(statistics) {
    const container = document.getElementById('department-report');
    
    if (statistics.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No data available</p>';
        return;
    }
    
    container.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <strong>Total Departments: ${statistics.length}</strong>
        </div>
        <div style="display: grid; gap: 1rem;">
            ${statistics.map(stat => `
                <div style="padding: 1rem; background: var(--background-color); border-radius: var(--radius-md); border-left: 4px solid var(--primary-color);">
                    <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">${stat.department}</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem; font-size: 0.875rem; color: var(--text-secondary);">
                        <div><strong>Employees:</strong> ${stat.employee_count}</div>
                        <div><strong>Avg Salary:</strong> $${stat.average_salary.toLocaleString()}</div>
                        <div><strong>Min:</strong> $${stat.min_salary.toLocaleString()}</div>
                        <div><strong>Max:</strong> $${stat.max_salary.toLocaleString()}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function updateSalaryReport(employees) {
    const container = document.getElementById('salary-report');
    
    if (employees.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No data available</p>';
        return;
    }
    
    // Calculate salary ranges
    const salaries = employees.map(emp => emp.salary).sort((a, b) => a - b);
    const min = salaries[0];
    const max = salaries[salaries.length - 1];
    const median = salaries[Math.floor(salaries.length / 2)];
    const average = Math.round(salaries.reduce((sum, sal) => sum + sal, 0) / salaries.length);
    
    // Create salary ranges
    const ranges = [
        { label: 'Under $50k', min: 0, max: 50000 },
        { label: '$50k - $75k', min: 50000, max: 75000 },
        { label: '$75k - $100k', min: 75000, max: 100000 },
        { label: 'Over $100k', min: 100000, max: Infinity }
    ];
    
    const rangeStats = ranges.map(range => {
        const count = employees.filter(emp => emp.salary >= range.min && emp.salary < range.max).length;
        const percentage = Math.round((count / employees.length) * 100);
        return { ...range, count, percentage };
    });
    
    container.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--primary-color);">$${average.toLocaleString()}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Average</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--success-color);">$${median.toLocaleString()}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Median</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--warning-color);">$${min.toLocaleString()}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Minimum</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--error-color);">$${max.toLocaleString()}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Maximum</div>
                </div>
            </div>
        </div>
        
        <div>
            <h4 style="margin-bottom: 1rem; color: var(--text-primary);">Salary Distribution</h4>
            ${rangeStats.map(range => `
                <div style="margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="font-weight: 500;">${range.label}</span>
                        <span style="color: var(--text-secondary);">${range.count} employees (${range.percentage}%)</span>
                    </div>
                    <div style="background: var(--border-color); height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: var(--primary-color); height: 100%; width: ${range.percentage}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('edit-modal');
    if (event.target === modal) {
        closeEditModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Escape key to close modal
    if (event.key === 'Escape') {
        closeEditModal();
    }
    
    // Ctrl+N to add new employee
    if (event.ctrlKey && event.key === 'n') {
        event.preventDefault();
        document.querySelector('[data-section="add-employee"]').click();
    }
    
    // Ctrl+F to focus search
    if (event.ctrlKey && event.key === 'f') {
        event.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

console.log('Employee Management System JavaScript loaded successfully!');
