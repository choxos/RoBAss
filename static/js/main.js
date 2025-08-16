// Main JavaScript for RoBAss Application

document.addEventListener('DOMContentLoaded', function() {
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

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

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

// Export functions for use in other scripts
window.RoBAss = {
    showToast: showToast,
    updateAssessmentProgress: updateAssessmentProgress,
    autoSaveResponse: autoSaveResponse,
    autoSaveJustification: autoSaveJustification
};
