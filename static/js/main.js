// Main JavaScript for ALSTOM MOC System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    initDatePickers();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize form validation
    initFormValidation();
    
    // Auto-save draft (if implemented)
    initAutoSave();
});

// Initialize date pickers
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'absolute';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
            
            this.currentTooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.currentTooltip && this.currentTooltip.parentNode) {
                this.currentTooltip.parentNode.removeChild(this.currentTooltip);
            }
        });
    });
}

// Initialize form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = 'var(--secondary-red)';
                    isValid = false;
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
        
        // Remove error border on input
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.style.borderColor = '';
            });
        });
    });
}

// Auto-save draft functionality
function initAutoSave() {
    const mocForm = document.querySelector('.moc-form');
    if (mocForm) {
        let saveTimer;
        
        mocForm.addEventListener('input', function() {
            clearTimeout(saveTimer);
            saveTimer = setTimeout(function() {
                // Show saving indicator
                const indicator = document.createElement('div');
                indicator.className = 'save-indicator';
                indicator.innerHTML = '<i class="fas fa-save"></i> Saving draft...';
                indicator.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: var(--primary-blue); color: white; padding: 10px 15px; border-radius: 6px; z-index: 1000;';
                document.body.appendChild(indicator);
                
                // Remove after 2 seconds
                setTimeout(() => {
                    if (indicator.parentNode) {
                        indicator.parentNode.removeChild(indicator);
                    }
                }, 2000);
            }, 2000); // Save after 2 seconds of inactivity
        });
    }
}

// Print functionality
function printMOC(mocId) {
    window.open('/moc/' + mocId + '/print', '_blank');
}

// Export to Excel
function exportToExcel() {
    alert('Export to Excel feature is coming soon!');
}

// Confirm before leaving page if form has changes
window.addEventListener('beforeunload', function(e) {
    const mocForm = document.querySelector('.moc-form');
    if (mocForm) {
        // Check if form has been modified
        const formData = new FormData(mocForm);
        let hasChanges = false;
        
        for (let pair of formData.entries()) {
            if (pair[1]) {
                hasChanges = true;
                break;
            }
        }
        
        if (hasChanges) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        }
    }
});

// Dynamic checklist counter
function updateChecklistCounter() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const counter = document.getElementById('checklist-counter');
    if (counter) {
        counter.textContent = `${checkboxes.length} items checked`;
    }
}

// Add styles for custom elements
const style = document.createElement('style');
style.textContent = `
    .custom-tooltip {
        background: var(--primary-dark);
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 10000;
        white-space: nowrap;
    }
    
    .save-indicator {
        animation: slideInUp 0.3s ease;
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .required-star {
        color: var(--secondary-red);
        margin-left: 4px;
    }
`;
document.head.appendChild(style);