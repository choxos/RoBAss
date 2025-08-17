// Main JavaScript for RoBAss Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark theme
    initializeThemeToggle();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 8 seconds (extended for better UX)
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 8000);

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Assessment form functionality
    initializeAssessmentForm();
    
    // Project management
    initializeProjectManagement();
    
    // Initialize smooth scrolling for navbar
    initializeSmoothScrolling();
});

function initializeAssessmentForm() {
    // Handle signalling question responses
    const responseButtons = document.querySelectorAll('.response-btn');
    responseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const questionContainer = this.closest('.signalling-question');
            const questionId = this.dataset.question;
            const response = this.dataset.response;
            
            // Remove active class from all buttons in this question
            questionContainer.querySelectorAll('.response-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Mark question as answered
            questionContainer.classList.add('answered');
            
            // Update hidden input if exists
            const hiddenInput = questionContainer.querySelector(`input[name="question_${questionId}"]`);
            if (hiddenInput) {
                hiddenInput.value = response;
            }
            
            // Auto-save if enabled
            if (window.autoSaveEnabled) {
                autoSaveResponse(questionId, response);
            }
        });
    });

    // Handle justification text areas
    const justificationTextareas = document.querySelectorAll('.justification-textarea');
    justificationTextareas.forEach(textarea => {
        textarea.addEventListener('blur', function() {
            const questionId = this.dataset.question;
            if (window.autoSaveEnabled) {
                autoSaveJustification(questionId, this.value);
            }
        });
    });

    // Progress tracking
    updateAssessmentProgress();
}

function initializeProjectManagement() {
    // Handle project deletion
    const deleteButtons = document.querySelectorAll('.delete-project-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const projectName = this.dataset.projectName;
            if (confirm(`Are you sure you want to delete the project "${projectName}"? This action cannot be undone.`)) {
                window.location.href = this.href;
            }
        });
    });

    // Handle study deletion
    const deleteStudyButtons = document.querySelectorAll('.delete-study-btn');
    deleteStudyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const studyTitle = this.dataset.studyTitle;
            if (confirm(`Are you sure you want to delete "${studyTitle}"? This action cannot be undone.`)) {
                window.location.href = this.href;
            }
        });
    });
}

function autoSaveResponse(questionId, response) {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/assessments/auto-save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            question_id: questionId,
            response: response
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Response saved automatically', 'success');
        }
    })
    .catch(error => {
        console.error('Auto-save failed:', error);
    });
}

function autoSaveJustification(questionId, justification) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/assessments/auto-save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            question_id: questionId,
            justification: justification
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Justification saved automatically', 'success');
        }
    });
}

function updateAssessmentProgress() {
    const totalQuestions = document.querySelectorAll('.signalling-question').length;
    const answeredQuestions = document.querySelectorAll('.signalling-question.answered').length;
    
    if (totalQuestions > 0) {
        const percentage = (answeredQuestions / totalQuestions) * 100;
        const progressBar = document.getElementById('assessment-progress');
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.textContent = Math.round(percentage) + '%';
        }
        
        // Update progress text
        const progressText = document.getElementById('progress-text');
        if (progressText) {
            progressText.textContent = `${answeredQuestions} of ${totalQuestions} questions answered`;
        }
    }
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Global setTheme function
function setTheme(theme) {
    const html = document.documentElement;
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    console.log('Setting theme to:', theme);
    
    html.setAttribute('data-bs-theme', theme);
    localStorage.setItem('robass-theme', theme);
    
    if (themeIcon) {
        if (theme === 'dark') {
            themeIcon.className = 'fas fa-sun';
            if (themeToggleBtn) {
                themeToggleBtn.title = 'Switch to Light Theme';
                themeToggleBtn.setAttribute('aria-label', 'Switch to Light Theme');
            }
        } else {
            themeIcon.className = 'fas fa-moon';
            if (themeToggleBtn) {
                themeToggleBtn.title = 'Switch to Dark Theme';
                themeToggleBtn.setAttribute('aria-label', 'Switch to Dark Theme');
            }
        }
    }
    
    // Update theme toggle button styling based on theme
    if (themeToggleBtn) {
        const baseClasses = 'btn rounded-circle position-fixed bottom-0 end-0 m-3 shadow-lg';
        if (theme === 'dark') {
            themeToggleBtn.className = `${baseClasses} btn-outline-light`;
        } else {
            themeToggleBtn.className = `${baseClasses} btn-outline-secondary`;
        }
        // Maintain the fixed attributes
        themeToggleBtn.style.zIndex = '1050';
        themeToggleBtn.style.width = '50px';
        themeToggleBtn.style.height = '50px';
    }
    
    console.log('Theme set successfully to:', theme);
}

// Theme Toggle Functionality
function initializeThemeToggle() {
    console.log('Initializing theme toggle...');
    
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const html = document.documentElement;
    
    console.log('Elements found:', {
        toggleBtn: !!themeToggleBtn,
        icon: !!themeIcon,
        html: !!html
    });
    
    if (!themeToggleBtn) {
        console.error('Theme toggle button not found!');
        return;
    }
    
    if (!themeIcon) {
        console.error('Theme icon not found!');
        return;
    }
    
    // Load saved theme or default to light
    const savedTheme = localStorage.getItem('robass-theme') || 'light';
    console.log('Loading saved theme:', savedTheme);
    setTheme(savedTheme);
    
    // Theme toggle button click handler
    themeToggleBtn.addEventListener('click', function(e) {
        console.log('Theme toggle clicked!', e);
        
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        console.log('Switching from', currentTheme, 'to', newTheme);
        setTheme(newTheme);
        
        // Add animation effect
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 150);
    });
    
    console.log('Theme toggle initialized successfully');
}

// Smooth scrolling for navbar links
function initializeSmoothScrolling() {
    // Add active nav link highlighting
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const currentLocation = location.pathname;
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
            link.closest('.nav-item').classList.add('active');
        }
    });
    
    // Handle navbar collapse on mobile after link click
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
    }
}

// Enhanced toast function with theme support
function showToast(message, type = 'info', duration = 5000) {
    // Create toast element
    const toast = document.createElement('div');
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    
    // Adjust colors for dark theme
    let toastClass = `toast align-items-center border-0`;
    let textClass = '';
    
    switch(type) {
        case 'success':
            toastClass += ' bg-success';
            textClass = 'text-white';
            break;
        case 'error':
        case 'danger':
            toastClass += ' bg-danger';
            textClass = 'text-white';
            break;
        case 'warning':
            toastClass += ' bg-warning';
            textClass = isDark ? 'text-black' : 'text-dark';
            break;
        case 'info':
        default:
            toastClass += ' bg-info';
            textClass = 'text-white';
            break;
    }
    
    toast.className = `${toastClass} ${textClass}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const closeButtonClass = textClass.includes('white') ? 'btn-close-white' : 'btn-close';
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${
                    type === 'success' ? 'check-circle' :
                    type === 'error' || type === 'danger' ? 'exclamation-triangle' :
                    type === 'warning' ? 'exclamation-circle' : 'info-circle'
                } me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close ${closeButtonClass} me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1060';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration
    });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
        
        // Remove container if empty
        if (toastContainer.children.length === 0) {
            toastContainer.remove();
        }
    });
}

// Export functions for use in other scripts
window.RoBAss = {
    showToast: showToast,
    updateAssessmentProgress: updateAssessmentProgress,
    autoSaveResponse: autoSaveResponse,
    autoSaveJustification: autoSaveJustification,
    setTheme: setTheme,
    initializeThemeToggle: initializeThemeToggle
};
