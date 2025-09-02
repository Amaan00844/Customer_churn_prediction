import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Customer Churn Analytics | Professional Dashboard", 
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Font Awesome, animations, and custom CSS for professional styling
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Enhanced Sidebar styling */
    .stSidebar {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    
    .stSidebar:hover {
        box-shadow: 5px 0 20px rgba(0,0,0,0.15);
    }
    
    /* Sidebar content styling */
    .stSidebar > div {
        background: transparent;
    }
    
    /* Sidebar when collapsed - hover to expand */
    .stSidebar[data-testid="stSidebar"][aria-expanded="false"] {
        width: 3rem !important;
        min-width: 3rem !important;
        transition: all 0.3s ease;
    }
    
    .stSidebar[data-testid="stSidebar"][aria-expanded="false"]:hover {
        width: 21rem !important;
        min-width: 21rem !important;
    }
    
    /* Sidebar toggle button styling */
    .stSidebar .css-1lcbmhc button {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stSidebar .css-1lcbmhc button:hover {
        background: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.3);
    }
    
    /* Floating action button for sidebar toggle */
    .sidebar-toggle {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 999;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    
    .sidebar-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Loading animation */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        backdrop-filter: blur(5px);
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid #e2e8f0;
        border-top: 4px solid #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Floating notification */
    .notification {
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: white;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 4px solid #10b981;
        z-index: 1000;
        animation: slideInRight 0.5s ease;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Progress bar */
    .progress-container {
        width: 100%;
        background: #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        font-weight: 300;
    }
    
    /* Professional card styling */
    .professional-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8ecf0;
        margin: 1rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 15px;
        padding: 2rem;
        border-left: 5px solid #3b82f6;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        color: #1e293b;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3b82f6;
    }
    
    .section-header i {
        color: #3b82f6;
        font-size: 1.5rem;
    }
    
    /* Form styling */
    .form-section {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .form-subsection {
        margin: 2rem 0;
        padding: 1.5rem;
        background: #f8fafc;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
    }
    
    .form-subsection h4 {
        color: #1e293b;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .form-subsection h4 i {
        color: #3b82f6;
    }
    
    /* Prediction results styling */
    .prediction-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .prediction-result {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .prediction-probability {
        color: rgba(255,255,255,0.9);
        font-size: 1.8rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .risk-high {
        background: #ef4444;
        color: white;
    }
    
    .risk-medium {
        background: #f59e0b;
        color: white;
    }
    
    .risk-low {
        background: #10b981;
        color: white;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.12);
    }
    
    .metric-icon {
        font-size: 2rem;
        color: #3b82f6;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Recommendations styling */
    .recommendation-card {
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    
    .recommendation-high {
        background: #fef2f2;
        border-left-color: #ef4444;
        color: #7f1d1d;
    }
    
    .recommendation-medium {
        background: #fffbeb;
        border-left-color: #f59e0b;
        color: #78350f;
    }
    
    .recommendation-low {
        background: #f0fdf4;
        border-left-color: #10b981;
        color: #14532d;
    }
    
    /* Input field styling */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    .stSlider > div > div > div {
        background: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    candidates = [os.path.join("models", "best_model_pipeline.pkl"), "best_model_pipeline.pkl"]
    for p in candidates:
        if os.path.isfile(p):
            with open(p, "rb") as f:
                return pickle.load(f)
    return None

model = load_model()

# Add JavaScript for enhanced interactivity
st.markdown("""
<script>
// Auto-expand sidebar on hover
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.css-1lcbmhc');
    if (sidebar) {
        sidebar.addEventListener('mouseenter', function() {
            this.style.width = '21rem';
        });
        sidebar.addEventListener('mouseleave', function() {
            this.style.width = '2.25rem';
        });
    }
});

// Smooth scroll to results
function scrollToResults() {
    setTimeout(() => {
        const resultsSection = document.querySelector('[data-testid="stMarkdownContainer"]');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }, 500);
}

// Show loading animation
function showLoading() {
    const loadingHTML = `
        <div class="loading-overlay">
            <div class="loading-spinner"></div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', loadingHTML);
    
    setTimeout(() => {
        const loading = document.querySelector('.loading-overlay');
        if (loading) loading.remove();
    }, 2000);
}
</script>
""", unsafe_allow_html=True)

# Professional Header Section with enhanced animations
st.markdown("""
<div class="main-header animate__animated animate__fadeInDown">
    <h1><i class="fas fa-chart-line"></i> Customer Churn Analytics</h1>
    <p>Advanced Machine Learning Dashboard for Customer Retention Intelligence</p>
    <div class="progress-container">
        <div class="progress-bar" style="width: 100%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Add floating action buttons and enhanced features
st.markdown("""
<div style="position: fixed; bottom: 2rem; right: 2rem; z-index: 1000; display: flex; flex-direction: column; gap: 1rem;">
    <button class="sidebar-toggle" onclick="toggleSidebar()" title="Toggle Sidebar">
        <i class="fas fa-bars"></i>
    </button>
    <button class="sidebar-toggle" onclick="scrollToTop()" title="Back to Top" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
        <i class="fas fa-arrow-up"></i>
    </button>
    <button class="sidebar-toggle" onclick="showHelp()" title="Help" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
        <i class="fas fa-question"></i>
    </button>
</div>

<script>
function toggleSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        const button = sidebar.querySelector('button');
        if (button) button.click();
    }
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showHelp() {
    const helpHTML = `
        <div class="notification" id="helpNotification">
            <h4><i class="fas fa-info-circle"></i> Quick Help</h4>
            <p>Fill out the customer information form and click "Analyze Customer Risk" to get predictions.</p>
            <button onclick="closeHelp()" style="background: none; border: none; float: right; cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', helpHTML);
    
    setTimeout(() => {
        const help = document.getElementById('helpNotification');
        if (help) help.remove();
    }, 5000);
}

function closeHelp() {
    const help = document.getElementById('helpNotification');
    if (help) help.remove();
}

// Form completion progress
function updateProgress() {
    const form = document.querySelector('[data-testid="stForm"]');
    if (form) {
        const inputs = form.querySelectorAll('select, input');
        const filled = Array.from(inputs).filter(input => input.value !== '').length;
        const progress = (filled / inputs.length) * 100;
        
        const progressBar = document.querySelector('.form-progress-bar');
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
    }
}

// Auto-save form data
function saveFormData() {
    const form = document.querySelector('[data-testid="stForm"]');
    if (form) {
        const formData = {};
        const inputs = form.querySelectorAll('select, input');
        inputs.forEach(input => {
            if (input.name) {
                formData[input.name] = input.value;
            }
        });
        localStorage.setItem('churnFormData', JSON.stringify(formData));
    }
}

// Load saved form data
function loadFormData() {
    const savedData = localStorage.getItem('churnFormData');
    if (savedData) {
        const formData = JSON.parse(savedData);
        Object.keys(formData).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = formData[key];
            }
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadFormData();
    
    // Add event listeners for form changes
    document.addEventListener('change', function(e) {
        if (e.target.closest('[data-testid="stForm"]')) {
            updateProgress();
            saveFormData();
        }
    });
    
    // Add smooth animations to metric cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
            }
        });
    });
    
    document.querySelectorAll('.metric-card').forEach(card => {
        observer.observe(card);
    });
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .form-progress-container {
        margin: 1rem 0;
        background: #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        height: 6px;
    }
    
    .form-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
        transition: width 0.3s ease;
        width: 0%;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);
</script>
""", unsafe_allow_html=True)

# Add form progress indicator
st.markdown("""
<div class="professional-card">
    <h4><i class="fas fa-tasks"></i> Form Completion Progress</h4>
    <div class="form-progress-container">
        <div class="form-progress-bar"></div>
    </div>
    <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">
        Complete all fields to get the most accurate prediction
    </p>
</div>
""", unsafe_allow_html=True)

# Professional Info Card
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="info-card">
        <h4><i class="fas fa-bullseye"></i> About This Platform</h4>
        <p>Our advanced analytics platform leverages machine learning algorithms to predict customer churn probability with high accuracy. 
        Input customer data to receive real-time risk assessments and actionable retention strategies.</p>
    </div>
    """, unsafe_allow_html=True)

if model is None:
    st.error("⚠️ Model not found. Please run: `python -m src.train` to train the model first.")
    st.stop()

# Professional Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <h3><i class="fas fa-list-check"></i> Quick Guide</h3>
        <ol>
            <li>Complete customer information form</li>
            <li>Click 'Analyze Customer Risk'</li>
            <li>Review prediction results</li>
            <li>Implement recommended actions</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-content">
        <h3><i class="fas fa-brain"></i> AI Model</h3>
        <p>Powered by advanced machine learning pipeline with feature engineering and ensemble methods.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-content">
        <h3><i class="fas fa-traffic-light"></i> Risk Classification</h3>
        <div style="margin: 0.5rem 0;">
            <span style="color: #10b981; font-weight: 600;"><i class="fas fa-circle"></i> Low Risk:</span> &lt; 30%
        </div>
        <div style="margin: 0.5rem 0;">
            <span style="color: #f59e0b; font-weight: 600;"><i class="fas fa-circle"></i> Medium Risk:</span> 30-70%
        </div>
        <div style="margin: 0.5rem 0;">
            <span style="color: #ef4444; font-weight: 600;"><i class="fas fa-circle"></i> High Risk:</span> &gt; 70%
        </div>
    </div>
    """, unsafe_allow_html=True)

# Professional Customer Information Form
st.markdown("---")
st.markdown('<div class="section-header"><i class="fas fa-user-circle"></i> Customer Information</div>', unsafe_allow_html=True)

with st.form("customer_form", clear_on_submit=False):
    # Demographics Section
    st.markdown("""
    <div class="form-subsection">
        <h4><i class="fas fa-users"></i> Demographics</h4>
    </div>
    """, unsafe_allow_html=True)
    
    demo_col1, demo_col2, demo_col3, demo_col4 = st.columns(4)
    
    with demo_col1:
        gender = st.selectbox("Gender", ["Male", "Female"], help="Customer's gender")
    with demo_col2:
        SeniorCitizen = st.selectbox("Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No", help="Is the customer a senior citizen?")
    with demo_col3:
        Partner = st.selectbox("Partner", ["Yes", "No"], help="Does the customer have a partner?")
    with demo_col4:
        Dependents = st.selectbox("Dependents", ["Yes", "No"], help="Does the customer have dependents?")

    # Account Information Section
    st.markdown("""
    <div class="form-subsection">
        <h4><i class="fas fa-credit-card"></i> Account Information</h4>
    </div>
    """, unsafe_allow_html=True)
    
    account_col1, account_col2, account_col3 = st.columns(3)
    
    with account_col1:
        tenure = st.slider("Tenure (months)", 0, 72, 12, help="How long the customer has been with the company")
    with account_col2:
        MonthlyCharges = st.number_input("Monthly Charges ($)", min_value=0.0, value=65.0, step=5.0, help="Customer's monthly charges")
    with account_col3:
        TotalCharges = st.number_input("Total Charges ($)", min_value=0.0, value=1500.0, step=50.0, help="Customer's total charges to date")

    # Services Section
    st.markdown("""
    <div class="form-subsection">
        <h4><i class="fas fa-cogs"></i> Services & Features</h4>
    </div>
    """, unsafe_allow_html=True)
    
    service_col1, service_col2 = st.columns(2)
    
    with service_col1:
        PhoneService = st.selectbox("Phone Service", ["Yes", "No"], help="Does the customer have phone service?")
        MultipleLines = st.selectbox("Multiple Lines", ["No", "Yes"], help="Does the customer have multiple phone lines?")
        InternetService = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"], help="Type of internet service")
        OnlineSecurity = st.selectbox("Online Security", ["No", "Yes"], help="Does the customer have online security?")
        OnlineBackup = st.selectbox("Online Backup", ["No", "Yes"], help="Does the customer have online backup?")

    with service_col2:
        DeviceProtection = st.selectbox("Device Protection", ["No", "Yes"], help="Does the customer have device protection?")
        TechSupport = st.selectbox("Tech Support", ["No", "Yes"], help="Does the customer have tech support?")
        StreamingTV = st.selectbox("Streaming TV", ["No", "Yes"], help="Does the customer have streaming TV?")
        StreamingMovies = st.selectbox("Streaming Movies", ["No", "Yes"], help="Does the customer have streaming movies?")

    # Contract & Billing Section
    st.markdown("""
    <div class="form-subsection">
        <h4><i class="fas fa-file-contract"></i> Contract & Billing</h4>
    </div>
    """, unsafe_allow_html=True)
    
    billing_col1, billing_col2 = st.columns(2)
    
    with billing_col1:
        Contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"], help="Customer's contract type")
        PaperlessBilling = st.selectbox("Paperless Billing", ["Yes", "No"], help="Does the customer use paperless billing?")
    with billing_col2:
        PaymentMethod = st.selectbox("Payment Method", [
            "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
        ], help="Customer's payment method")

    st.markdown("---")
    submitted = st.form_submit_button("🔍 Analyze Customer Risk", use_container_width=True, type="primary")

if submitted:
    input_df = pd.DataFrame([{ 
        'gender': gender,
        'SeniorCitizen': SeniorCitizen,
        'Partner': Partner,
        'Dependents': Dependents,
        'tenure': tenure,
        'PhoneService': PhoneService,
        'MultipleLines': MultipleLines,
        'InternetService': InternetService,
        'OnlineSecurity': OnlineSecurity,
        'OnlineBackup': OnlineBackup,
        'DeviceProtection': DeviceProtection,
        'TechSupport': TechSupport,
        'StreamingTV': StreamingTV,
        'StreamingMovies': StreamingMovies,
        'Contract': Contract,
        'PaperlessBilling': PaperlessBilling,
        'PaymentMethod': PaymentMethod,
        'MonthlyCharges': MonthlyCharges,
        'TotalCharges': TotalCharges,
    }])

    if model is None:
        st.error("Model not loaded.")
    else:
        try:
            pred = int(model.predict(input_df)[0])
            proba = float(model.predict_proba(input_df)[0][1])
            
            # Professional Results Section
            st.markdown("---")
            st.markdown('<div class="section-header"><i class="fas fa-analytics"></i> Analysis Results</div>', unsafe_allow_html=True)
            
            # Main prediction display
            result_col1, result_col2, result_col3 = st.columns([1, 2, 1])
            
            with result_col2:
                # Determine styling based on prediction
                if pred == 1:
                    churn_icon = "fas fa-exclamation-triangle"
                    churn_text = "CUSTOMER WILL CHURN"
                    churn_class = "prediction-result-danger"
                else:
                    churn_icon = "fas fa-check-circle"
                    churn_text = "CUSTOMER WILL STAY"
                    churn_class = "prediction-result-success"
                
                # Risk level styling
                if proba > 0.7:
                    risk_class = "risk-high"
                    risk_text = "HIGH RISK"
                    risk_icon = "fas fa-exclamation-circle"
                elif proba > 0.3:
                    risk_class = "risk-medium"
                    risk_text = "MEDIUM RISK"
                    risk_icon = "fas fa-exclamation-triangle"
                else:
                    risk_class = "risk-low"
                    risk_text = "LOW RISK"
                    risk_icon = "fas fa-check-circle"
                
                st.markdown(f"""
                <div class="prediction-container">
                    <div class="prediction-result">
                        <i class="{churn_icon}"></i> {churn_text}
                    </div>
                    <div class="prediction-probability">
                        Churn Probability: {proba:.1%}
                    </div>
                    <div class="risk-badge {risk_class}">
                        <i class="{risk_icon}"></i> {risk_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Professional Metrics Cards
            st.markdown("""
            <div class="section-header">
                <i class="fas fa-chart-bar"></i> Key Metrics
            </div>
            """, unsafe_allow_html=True)
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-bullseye"></i></div>
                    <div class="metric-value">{"Will Churn" if pred == 1 else "Will Stay"}</div>
                    <div class="metric-label">Prediction</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-percentage"></i></div>
                    <div class="metric-value">{proba:.1%}</div>
                    <div class="metric-label">Churn Probability</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col3:
                confidence = abs(proba - 0.5) * 2
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="metric-value">{confidence:.1%}</div>
                    <div class="metric-label">Confidence Level</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon"><i class="{risk_icon}"></i></div>
                    <div class="metric-value">{risk_text.title()}</div>
                    <div class="metric-label">Risk Assessment</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Interactive Probability Gauge
            st.markdown("""
            <div class="section-header">
                <i class="fas fa-tachometer-alt"></i> Risk Probability Gauge
            </div>
            """, unsafe_allow_html=True)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = proba * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Churn Risk Probability (%)", 'font': {'size': 20, 'color': '#1e293b'}},
                delta = {'reference': 50, 'increasing': {'color': "#ef4444"}, 'decreasing': {'color': "#10b981"}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#64748b"},
                    'bar': {'color': "#3b82f6", 'thickness': 0.3},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e2e8f0",
                    'steps': [
                        {'range': [0, 30], 'color': "#dcfce7"},
                        {'range': [30, 70], 'color': "#fef3c7"},
                        {'range': [70, 100], 'color': "#fee2e2"}
                    ],
                    'threshold': {
                        'line': {'color': "#ef4444", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            
            fig.update_layout(
                height=400,
                font={'color': "#1e293b", 'family': "Inter"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Professional Recommendations
            st.markdown("""
            <div class="section-header">
                <i class="fas fa-lightbulb"></i> Strategic Recommendations
            </div>
            """, unsafe_allow_html=True)
            
            if proba > 0.7:
                st.markdown(f"""
                <div class="recommendation-card recommendation-high">
                    <h4><i class="fas fa-exclamation-triangle"></i> HIGH RISK - Immediate Action Required</h4>
                    <ul>
                        <li><strong>Immediate Contact:</strong> Reach out within 24 hours with retention offer</li>
                        <li><strong>Account Review:</strong> Investigate service issues and billing concerns</li>
                        <li><strong>Loyalty Program:</strong> Enroll in premium loyalty benefits</li>
                        <li><strong>Contract Extension:</strong> Offer attractive long-term contract with discounts</li>
                        <li><strong>Executive Escalation:</strong> Assign dedicated account manager</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif proba > 0.3:
                st.markdown(f"""
                <div class="recommendation-card recommendation-medium">
                    <h4><i class="fas fa-eye"></i> MEDIUM RISK - Proactive Monitoring</h4>
                    <ul>
                        <li><strong>Proactive Outreach:</strong> Schedule customer satisfaction check-in</li>
                        <li><strong>Service Review:</strong> Assess current service utilization and satisfaction</li>
                        <li><strong>Targeted Offers:</strong> Present relevant promotions and upgrades</li>
                        <li><strong>Usage Monitoring:</strong> Track service usage patterns for early warning signs</li>
                        <li><strong>Feedback Collection:</strong> Gather detailed feedback on service experience</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="recommendation-card recommendation-low">
                    <h4><i class="fas fa-check-circle"></i> LOW RISK - Customer Stable</h4>
                    <ul>
                        <li><strong>Standard Service:</strong> Continue providing excellent service quality</li>
                        <li><strong>Upselling Opportunities:</strong> Explore additional service offerings</li>
                        <li><strong>Quality Maintenance:</strong> Ensure consistent service delivery</li>
                        <li><strong>Satisfaction Surveys:</strong> Include in regular satisfaction assessments</li>
                        <li><strong>Referral Programs:</strong> Encourage customer referrals with incentives</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            st.info("Please check that all fields are filled correctly and try again.")
