// ============================================
// FRAUD DETECTION SYSTEM - JAVASCRIPT
// ============================================

// Auto-populate hour with current time on page load
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('hour').value = new Date().getHours();
});

// Get form elements
const fraudForm = document.getElementById('fraudForm');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultCard = document.getElementById('resultCard');
const formCard = document.querySelector('.form-card');

// Form submission handler
fraudForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const formData = {
        amount: parseFloat(document.getElementById('amount').value),
        transaction_type: document.getElementById('transaction_type').value,
        merchant_category: document.getElementById('merchant_category').value,
        country: document.getElementById('country').value,
        hour: parseInt(document.getElementById('hour').value)
    };
    
    // Validate all fields
    if (!formData.amount || !formData.transaction_type || 
        !formData.merchant_category || !formData.country || 
        formData.hour === null || formData.hour === undefined) {
        showToast('⚠️ Please fill in all fields', 'warning');
        return;
    }
    
    // Show loading
    loadingOverlay.classList.add('active');
    
    try {
        // Send prediction request
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        // Hide loading
        loadingOverlay.classList.remove('active');
        
        if (result.success) {
            // Display results
            displayResult(result, formData);
        } else {
            showToast('❌ ' + result.message, 'error');
        }
        
    } catch (error) {
        loadingOverlay.classList.remove('active');
        showToast('❌ Network error. Please try again.', 'error');
        console.error('Error:', error);
    }
});

// Display prediction result
function displayResult(result, formData) {
    // Show result card next to form (flex side-by-side)
    resultCard.style.display = 'block';
    formCard.style.display = 'block';
    
    // Scroll to top of main content
    document.querySelector('.main-content').scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Set timestamp
    document.getElementById('timestamp').textContent = result.timestamp;
    
    // Main result
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    
    if (result.is_fraud === 1) {
        // Fraud detected
        resultIcon.innerHTML = '🚨';
        resultIcon.className = 'result-icon fraud';
        resultTitle.textContent = 'Fraud Detected';
        resultTitle.className = 'result-title fraud';
        resultMessage.textContent = 'This transaction shows signs of fraudulent activity. Please review carefully.';
    } else {
        // Genuine transaction
        resultIcon.innerHTML = '✅';
        resultIcon.className = 'result-icon genuine';
        resultTitle.textContent = 'Transaction Genuine';
        resultTitle.className = 'result-title genuine';
        resultMessage.textContent = 'This transaction appears to be legitimate and safe.';
    }
    
    // Fraud probability meter
    const probabilityValue = document.getElementById('probabilityValue');
    const meterFill = document.getElementById('meterFill');
    
    probabilityValue.textContent = result.fraud_probability + '%';
    meterFill.style.width = result.fraud_probability + '%';
    
    // Set meter color based on probability
    if (result.fraud_probability >= 70) {
        meterFill.style.background = '#e74c3c';
    } else if (result.fraud_probability >= 40) {
        meterFill.style.background = '#f39c12';
    } else {
        meterFill.style.background = '#2ecc71';
    }
    
    // Risk level badge
    const riskBadge = document.getElementById('riskBadge');
    const riskLevel = document.getElementById('riskLevel');
    
    riskLevel.textContent = result.risk_level;
    riskBadge.style.background = result.risk_color;
    // ⭐ ADD THIS: Display Explanation
if (result.explanation && result.explanation.length > 0) {
    const explanationSection = document.getElementById('explanationSection');
    const explanationList = document.getElementById('explanationList');
    
    explanationSection.style.display = 'block';
    explanationList.innerHTML = '';
    
    result.explanation.forEach((item, index) => {
        const icon = item.risk_level === 'high' ? '🚨' : 
                     item.risk_level === 'medium' ? '⚠️' : '✅';
        
        const riskClass = item.risk_level || 'low';
        
        const explanationItem = document.createElement('div');
        explanationItem.className = `explanation-item risk-${riskClass}`;
        explanationItem.innerHTML = `
            <div class="explanation-icon">${icon}</div>
            <div class="explanation-content">
                <div class="explanation-factor">${item.factor}</div>
                <div class="explanation-value">Value: ${item.value}</div>
                <div class="explanation-importance">
                    Importance: ${(item.importance * 100).toFixed(1)}%
                    <span class="explanation-badge ${riskClass}">
                        ${riskClass === 'high' ? 'High Risk' : riskClass === 'medium' ? 'Medium Risk' : 'Low Risk'}
                    </span>
                </div>
            </div>
        `;
        explanationList.appendChild(explanationItem);
    });
} else {
    document.getElementById('explanationSection').style.display = 'none';
}

// Transaction summary (existing code continues here...)
document.getElementById('summaryAmount').textContent = '$' + formData.amount.toFixed(2);
    // Transaction summary
    document.getElementById('summaryAmount').textContent = '$' + formData.amount.toFixed(2);
    document.getElementById('summaryType').textContent = formData.transaction_type;
    document.getElementById('summaryMerchant').textContent = formData.merchant_category;
    document.getElementById('summaryCountry').textContent = formData.country;
    document.getElementById('summaryHour').textContent = formatHour(formData.hour);
}

// Format hour for display
function formatHour(hour) {
    if (hour === 0) return '12:00 AM';
    if (hour < 12) return hour + ':00 AM';
    if (hour === 12) return '12:00 PM';
    return (hour - 12) + ':00 PM';
}

// Reset form and show input again
function resetForm() {
    // Reset form fields
    fraudForm.reset();
    
    // Hide result card, keep form centered
    resultCard.style.display = 'none';
    formCard.style.display = 'block';
    document.getElementById('explanationSection').style.display = 'none';

    
    // Restore current hour
    document.getElementById('hour').value = new Date().getHours();
    
    // Scroll to form
    formCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Show a toast notification
function showToast(message, type = 'error') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), 4000);
}

// Auto-fill current hour on page load
window.addEventListener('DOMContentLoaded', () => {
    const currentHour = new Date().getHours();
    document.getElementById('hour').value = currentHour;
});

// Input validation - only positive numbers for amount
document.getElementById('amount').addEventListener('input', (e) => {
    if (e.target.value < 0) {
        e.target.value = 0;
    }
});

// Input validation - hour between 0-23
document.getElementById('hour').addEventListener('input', (e) => {
    if (e.target.value < 0) {
        e.target.value = 0;
    } else if (e.target.value > 23) {
        e.target.value = 23;
    }
});

// Add visual feedback on form field changes
const formInputs = document.querySelectorAll('input, select');
formInputs.forEach(input => {
    input.addEventListener('focus', (e) => {
        e.target.parentElement.style.transform = 'scale(1.01)';
        e.target.parentElement.style.transition = 'transform 0.2s ease';
    });
    
    input.addEventListener('blur', (e) => {
        e.target.parentElement.style.transform = 'scale(1)';
    });
});
