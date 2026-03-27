// Process Change Management Dashboard - Main Script

// Admin state management
let isAdminMode = false;
let customDate = null;
let customTime = null;
let timeFormat = '12';

// DOM Elements
const dateTimeElement = document.getElementById('currentDateTime');
const adminBadge = document.getElementById('adminBadge');
const adminPanel = document.getElementById('adminPanel');
const adminOverlay = document.getElementById('adminOverlay');
const systemTimeElement = document.getElementById('systemTime');

// Admin panel elements
const adminDateInput = document.getElementById('adminDate');
const adminTimeInput = document.getElementById('adminTime');
const timeFormatSelect = document.getElementById('timeFormat');

// Initialize current date/time
function initCurrentDateTime() {
    const now = new Date();
    adminDateInput.value = now.toISOString().split('T')[0];
    adminTimeInput.value = now.toTimeString().substring(0, 5);
}

// Open admin panel
function openAdminPanel() {
    isAdminMode = true;
    adminPanel.classList.add('active');
    adminOverlay.classList.add('active');
    dateTimeElement.classList.add('admin-mode');
    adminBadge.style.display = 'block';
    
    // Initialize inputs with current display time
    const displayText = dateTimeElement.textContent;
    const [datePart, timePart] = displayText.split(' ');
    
    // Parse date
    const [month, day, year] = datePart.split('/');
    adminDateInput.value = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    
    // Parse time
    if (timePart.includes('AM') || timePart.includes('PM')) {
        let [time, ampm] = timePart.split(' ');
        let [hours, minutes] = time.split(':');
        
        if (ampm === 'PM' && hours !== '12') {
            hours = parseInt(hours) + 12;
        } else if (ampm === 'AM' && hours === '12') {
            hours = '00';
        }
        
        adminTimeInput.value = `${hours.toString().padStart(2, '0')}:${minutes}`;
        timeFormatSelect.value = '12';
    } else {
        adminTimeInput.value = timePart;
        timeFormatSelect.value = '24';
    }
}

// Close admin panel
function closeAdminPanel() {
    adminPanel.classList.remove('active');
    adminOverlay.classList.remove('active');
}

// Save time changes
function saveTimeChanges() {
    customDate = adminDateInput.value;
    customTime = adminTimeInput.value;
    timeFormat = timeFormatSelect.value;
    
    updateDisplayTime();
    closeAdminPanel();
}

// Reset to current time
function resetToCurrent() {
    const now = new Date();
    
    // Reset inputs to current time
    adminDateInput.value = now.toISOString().split('T')[0];
    adminTimeInput.value = now.toTimeString().substring(0, 5);
    timeFormatSelect.value = '12';
    
    // Clear custom settings
    customDate = null;
    customTime = null;
    timeFormat = '12';
    
    // Update display
    updateDisplayTime();
    dateTimeElement.classList.remove('admin-mode');
    adminBadge.style.display = 'none';
    isAdminMode = false;
}

// Format time based on settings
function formatCustomTime(date) {
    let hours = date.getHours();
    const minutes = date.getMinutes();
    
    if (timeFormat === '12') {
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // Convert 0 to 12
        const minutesStr = minutes.toString().padStart(2, '0');
        return `${hours}:${minutesStr} ${ampm}`;
    } else {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    }
}

// Update display time
function updateDisplayTime() {
    let displayDate;
    
    if (customDate && customTime && isAdminMode) {
        // Use admin-set time
        const [year, month, day] = customDate.split('-');
        const [hours, minutes] = customTime.split(':');
        displayDate = new Date(year, month - 1, day, hours, minutes);
    } else {
        // Use current time
        displayDate = new Date();
    }
    
    // Format date
    const dateStr = displayDate.toLocaleDateString('en-US', {
        month: 'numeric',
        day: 'numeric',
        year: 'numeric'
    });
    
    // Format time
    let timeStr;
    if (isAdminMode && customDate && customTime) {
        timeStr = formatCustomTime(displayDate);
    } else {
        timeStr = displayDate.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
    
    // Update display
    dateTimeElement.textContent = `${dateStr} ${timeStr}`;
}

// Update system time (real time)
function updateSystemTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    systemTimeElement.textContent = timeStr;
}

// Initialize button interactions
function initButtonInteractions() {
    // Card buttons
    const cardButtons = document.querySelectorAll('.card .btn');
    cardButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Add click animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
            
            // Show notification
            showNotification('Action triggered: ' + this.textContent.trim());
        });
    });
    
    // Database button
    const dbButton = document.querySelector('.db-btn');
    if (dbButton) {
        dbButton.addEventListener('click', function() {
            showNotification('Accessing PCRN Database...');
        });
    }
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--alstom-blue);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1001;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add notification animations
function addNotificationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize the application
function init() {
    // Initialize current date/time
    initCurrentDateTime();
    
    // Initialize time displays
    updateDisplayTime();
    updateSystemTime();
    
    // Initialize button interactions
    initButtonInteractions();
    
    // Add notification styles
    addNotificationStyles();
    
    // Update time every second
    setInterval(() => {
        updateSystemTime();
        if (!isAdminMode) {
            updateDisplayTime();
        }
    }, 1000);
    
    // Close admin panel on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAdminPanel();
        }
    });
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);