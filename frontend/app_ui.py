import streamlit as st
import requests
import os
import streamlit.components.v1 as components

# Configure the page title and layout
st.set_page_config(page_title="Logistics Control Center", layout="wide")

# Get FastAPI backend URL dynamically from environment
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
FASTAPI_CLIENT_URL = os.getenv("FASTAPI_CLIENT_URL", FASTAPI_URL)
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@omnistream.com")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id_here")

# Check for Google Sign-In token parameter in URL
query_params = st.query_params
if "token" in query_params:
    st.session_state["token"] = query_params["token"]
    st.query_params.clear()
    st.toast("Signed in with Google successfully!", icon="🔑")
    st.rerun()

# Initialize session state for theme
if "theme" not in st.session_state:
    st.session_state["theme"] = "Dark"

# Theme selector at the very top of the sidebar
st.sidebar.markdown("### 🎨 Theme Settings")
selected_theme = st.sidebar.selectbox(
    "Choose Mode",
    ["Dark", "Light"],
    index=0 if st.session_state["theme"] == "Dark" else 1,
    key="theme_selector"
)
st.session_state["theme"] = selected_theme

# Define theme colors dynamically based on the state variable
if st.session_state["theme"] == "Dark":
    theme_css = """
    :root {
        --st-background-color: #0e1117 !important;
        --st-text-color: #e0e6ed !important;
        --st-secondary-background-color: #161b22 !important;
        --st-primary-color: #00f0ff !important;
        --card-border: rgba(255, 255, 255, 0.15) !important;
    }
    """
    google_btn_bg = "#1d212a"
    google_btn_color = "#e0e6ed"
    google_btn_border = "rgba(255, 255, 255, 0.15)"
    google_btn_hover = "#242936"
else:
    theme_css = """
    :root {
        --st-background-color: #ffffff !important;
        --st-text-color: #1f2937 !important;
        --st-secondary-background-color: #f3f4f6 !important;
        --st-primary-color: #0088cc !important;
        --card-border: rgba(0, 0, 0, 0.12) !important;
    }
    """
    google_btn_bg = "#ffffff"
    google_btn_color = "#1f1f1f"
    google_btn_border = "#dadce0"
    google_btn_hover = "#f8f9fa"

# Inject custom CSS for premium UI styling and theme compliance
st.markdown(f"""
<style>
{theme_css}

/* 1. Global Page Aesthetics & Theme Integration */
.stApp {{
    background-color: var(--st-background-color) !important;
    color: var(--st-text-color) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}}

/* Seamless Sidebar background matching the main page */
section[data-testid="stSidebar"] {{
    background-color: var(--st-background-color) !important;
    border-right: 1px solid var(--card-border) !important;
}}

/* Sidebar inner content padding to prevent cramped spacing */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    padding: 2.5rem 1.5rem !important;
}}

/* Improve header separation */
h1 {{
    font-weight: 700 !important;
    font-size: 2.2rem !important;
    margin-bottom: 0.5rem !important;
    letter-spacing: -0.02em !important;
}}

/* 2. Form Control Labels Contrast Fixes */
label, [data-testid="stWidgetLabel"] p {{
    color: var(--st-text-color) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.015em;
    opacity: 0.95;
    margin-bottom: 0.4rem !important;
}}

/* 3. Text inputs visual improvements */
div[data-testid="stTextInput"] input {{
    border-radius: 8px !important;
    border: 1px solid var(--card-border) !important;
    background-color: var(--st-secondary-background-color) !important;
    color: var(--st-text-color) !important;
    padding: 0.5rem 0.75rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: var(--st-primary-color) !important;
    box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.15) !important;
}}

/* 4. Button Styling with dynamic text adjustment */
div.stButton > button {{
    color: var(--st-text-color) !important;
    background-color: var(--st-secondary-background-color) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease-in-out !important;
    width: 100%;
}}
div.stButton > button:hover {{
    border-color: var(--st-primary-color) !important;
    color: var(--st-primary-color) !important;
    background-color: var(--st-background-color) !important;
}}

/* Primary Button Styling */
div.stButton > button[kind="primary"] {{
    background-color: var(--st-primary-color) !important;
    color: #ffffff !important; /* Force high-contrast white text for primary actions */
    border: 1px solid var(--st-primary-color) !important;
    font-weight: 600 !important;
}}
div.stButton > button[kind="primary"]:hover {{
    opacity: 0.9 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0, 240, 255, 0.2) !important;
}}

/* 5. Custom Card Styling for Container Layouts */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
    padding: 1.75rem !important;
    background-color: var(--st-secondary-background-color) !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    margin-bottom: 1.5rem !important;
}}

/* 6. Clean Google Button container */
iframe[title="streamlit_components.v1.html"] {{
    border: none !important;
    background: transparent !important;
    margin-top: 0.5rem !important;
}}

/* Password eye toggle buttons alignment */
div[data-testid="column"] button {{
    border: 1px solid var(--card-border) !important;
    background-color: var(--st-secondary-background-color) !important;
    border-radius: 6px !important;
    height: 40px !important;
    margin-top: 28px !important;
    padding: 0 !important;
}}
</style>
""", unsafe_allow_html=True)

# Helper function for password input with an eye-toggle button
def password_input(label: str, key: str):
    state_key = f"show_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = False
        
    is_visible = st.session_state[state_key]
    
    col1, col2 = st.columns([5, 1])
    with col1:
        pwd = st.text_input(label, type="default" if is_visible else "password", key=f"val_{key}")
    with col2:
        icon = "👁️" if is_visible else "🙈"
        if st.button(icon, key=f"toggle_{key}", use_container_width=True):
            st.session_state[state_key] = not st.session_state[state_key]
            st.rerun()
    return pwd

# Initialize session state variables
if "token" not in st.session_state:
    st.session_state["token"] = None

if "auth_flow" not in st.session_state:
    st.session_state["auth_flow"] = "login"

if "temp_email" not in st.session_state:
    st.session_state["temp_email"] = ""

# ==========================================
# SIDEBAR: User Authentication System
# ==========================================
st.sidebar.header("🔐 User Authentication")

# Render active flow state machine
if st.session_state["token"] is None:
    flow = st.session_state["auth_flow"]

    # ------------------
    # FLOW: LOGIN & REGISTRATION
    # ------------------
    if flow == "login":
        auth_tab, register_tab = st.sidebar.tabs(["Login", "Register"])
        
        with auth_tab:
            username = st.text_input("Username or Email", key="login_user")
            password = password_input("Password", key="login_pass")
            
            if st.button("Sign In", type="primary", use_container_width=True):
                if username and password:
                    try:
                        login_payload = {"username": username, "password": password}
                        response = requests.post(f"{FASTAPI_URL}/auth/login", data=login_payload)
                        
                        if response.status_code == 200:
                            st.session_state["token"] = response.json().get("access_token")
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            detail = response.json().get("detail", "Invalid credentials.")
                            st.error(detail)
                    except Exception as e:
                        st.error(f"Auth Backend unreachable: {e}")
                else:
                    st.warning("Please fill out all fields.")
            
            # Forgot Password Button Link
            if st.button("Forgot Password?", use_container_width=True, type="secondary"):
                st.session_state["auth_flow"] = "forgot_password"
                st.rerun()

        with register_tab:
            new_username = st.text_input("Choose Username", key="reg_user")
            new_email = st.text_input("Email Address", key="reg_email")
            new_password = password_input("Choose Password", key="reg_pass")
            confirm_password = password_input("Confirm Password", key="reg_pass_conf")
            
            if st.button("Create Account", type="primary", use_container_width=True):
                if new_username and new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        try:
                            register_payload = {
                                "username": new_username,
                                "email": new_email,
                                "password": new_password
                            }
                            response = requests.post(f"{FASTAPI_URL}/auth/register", json=register_payload)
                            
                            if response.status_code == 201:
                                st.session_state["temp_email"] = new_email
                                st.session_state["auth_flow"] = "verify_registration"
                                st.success("Account created! Check console/email for OTP.")
                                st.rerun()
                            else:
                                err_detail = response.json().get("detail", "Registration failed.")
                                st.error(err_detail)
                        except Exception as e:
                            st.error(f"Auth Backend unreachable: {e}")
                else:
                    st.warning("Please fill out all fields.")

        # ------------------
        # GOOGLE OAUTH SIGN-IN BUTTON (Cleaned & Integrated)
        # ------------------
        st.sidebar.markdown("---")
        st.sidebar.caption("Or authenticate with:")
        
        is_mock = (
            not GOOGLE_CLIENT_ID or 
            "your_google_client_id" in GOOGLE_CLIENT_ID or 
            GOOGLE_CLIENT_ID == ""
        )
        
        if is_mock:
            # Render Mock Google Button with dynamic light/dark theming
            mock_html = """
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: transparent;
                }
                .g-btn {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: {GOOGLE_BTN_BG};
                    color: {GOOGLE_BTN_COLOR};
                    border: 1px solid {GOOGLE_BTN_BORDER};
                    border-radius: 8px;
                    padding: 10px 12px;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    cursor: pointer;
                    width: 100%;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                    transition: all 0.2s;
                }
                .g-btn:hover {
                    background-color: {GOOGLE_BTN_HOVER};
                }
            </style>
            <div style="width: 100%;">
                <button class="g-btn" onclick="mockSignIn()">
                    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" viewBox="0 0 48 48" style="margin-right: 10px; display: block; flex-shrink: 0;">
                        <g>
                            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                            <path fill="#4285F4" d="M46.5 24c0-1.61-.15-3.16-.42-4.69H24v8.89h12.63c-.55 2.89-2.18 5.33-4.62 6.96l7.18 5.56C43.43 36.27 46.5 30.73 46.5 24z"></path>
                            <path fill="#FBBC05" d="M10.54 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.98-6.19z"></path>
                            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.18-5.56c-2.03 1.36-4.63 2.17-8.71 2.17-6.26 0-11.57-4.22-13.46-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                            <polygon points="0 0 48 0 48 48 0 48" fill="none"></polygon>
                        </g>
                    </svg>
                    Sign in with Google
                </button>
            </div>
            <script>
                function mockSignIn() {
                    var email = prompt("Enter a mock email to authenticate with Google:", "john.doe@gmail.com");
                    if (email) {
                        fetch("{FASTAPI_CLIENT_URL}/auth/google-login", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({ id_token: email })
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.access_token) {
                                window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + "?token=" + data.access_token;
                            } else {
                                alert("Auth failed: " + JSON.stringify(data));
                            }
                        })
                        .catch(err => alert("Error connecting to backend: " + err));
                    }
                }
            </script>
            """.replace("{FASTAPI_CLIENT_URL}", FASTAPI_CLIENT_URL).replace("{GOOGLE_BTN_BG}", google_btn_bg).replace("{GOOGLE_BTN_COLOR}", google_btn_color).replace("{GOOGLE_BTN_BORDER}", google_btn_border).replace("{GOOGLE_BTN_HOVER}", google_btn_hover)
            components.html(mock_html, height=50)
        else:
            # Render Real Google Button
            google_html = """
            <script src="https://accounts.google.com/gsi/client" async defer></script>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: transparent;
                }
            </style>
            <div id="g_id_onload"
                 data-client_id="{GOOGLE_CLIENT_ID}"
                 data-context="signin"
                 data-ux_mode="popup"
                 data-callback="handleCredentialResponse"
                 data-auto_prompt="false">
            </div>
            <div class="g_id_signin"
                 data-type="standard"
                 data-shape="rectangular"
                 data-theme="outline"
                 data-text="signin_with"
                 data-size="large"
                 data-logo_alignment="left"
                 style="width: 100%;">
            </div>
            <script>
                function handleCredentialResponse(response) {
                    fetch("{FASTAPI_CLIENT_URL}/auth/google-login", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ id_token: response.credential })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.access_token) {
                            window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + "?token=" + data.access_token;
                        } else {
                            alert("Google auth failed on backend");
                        }
                    })
                    .catch(err => alert("Error connecting to backend: " + err));
                }
            </script>
            """.replace("{FASTAPI_CLIENT_URL}", FASTAPI_CLIENT_URL).replace("{GOOGLE_CLIENT_ID}", GOOGLE_CLIENT_ID)
            components.html(google_html, height=50)

    # ------------------
    # FLOW: VERIFY REGISTRATION OTP
    # ------------------
    elif flow == "verify_registration":
        st.sidebar.subheader("📩 Verify Email Address")
        st.sidebar.write(f"An OTP verification code was sent to: **{st.session_state['temp_email']}**")
        st.sidebar.caption("(Check backend console logs if running locally with mock email)")
        
        otp_code = st.sidebar.text_input("Enter 6-digit OTP Code", max_chars=6)
        
        if st.sidebar.button("Verify Code", type="primary", use_container_width=True):
            if otp_code:
                try:
                    payload = {
                        "email": st.session_state["temp_email"],
                        "code": otp_code,
                        "purpose": "register"
                    }
                    response = requests.post(f"{FASTAPI_URL}/auth/verify-otp", json=payload)
                    
                    if response.status_code == 200:
                        st.sidebar.success("🎉 Account verified successfully!")
                        st.session_state["auth_flow"] = "login"
                        st.session_state["temp_email"] = ""
                        st.rerun()
                    else:
                        st.sidebar.error(response.json().get("detail", "Verification failed."))
                except Exception as e:
                    st.sidebar.error(f"Error connecting to backend: {e}")
            else:
                st.sidebar.warning("Please enter the code.")
                
        if st.sidebar.button("Cancel & Return to Login", use_container_width=True):
            st.session_state["auth_flow"] = "login"
            st.session_state["temp_email"] = ""
            st.rerun()

    # ------------------
    # FLOW: FORGOT PASSWORD
    # ------------------
    elif flow == "forgot_password":
        st.sidebar.subheader("🔑 Request Password Reset")
        reset_email = st.sidebar.text_input("Enter your Registered Email")
        
        if st.sidebar.button("Send Reset OTP", type="primary", use_container_width=True):
            if reset_email:
                try:
                    payload = {"email": reset_email}
                    response = requests.post(f"{FASTAPI_URL}/auth/forgot-password", json=payload)
                    
                    if response.status_code == 200:
                        st.session_state["temp_email"] = reset_email
                        st.session_state["auth_flow"] = "reset_password"
                        st.sidebar.success("Reset OTP triggered! Check console/email.")
                        st.rerun()
                    else:
                        st.sidebar.error(response.json().get("detail", "Request failed."))
                except Exception as e:
                    st.sidebar.error(f"Error connecting to backend: {e}")
            else:
                st.sidebar.warning("Please enter your email.")
                
        if st.sidebar.button("Cancel & Return", use_container_width=True):
            st.session_state["auth_flow"] = "login"
            st.session_state["temp_email"] = ""
            st.rerun()

    # ------------------
    # FLOW: RESET PASSWORD
    # ------------------
    elif flow == "reset_password":
        st.sidebar.subheader("🔒 Reset Password")
        st.sidebar.write(f"Resetting password for: **{st.session_state['temp_email']}**")
        st.sidebar.caption("(Check backend console logs for OTP)")
        
        reset_otp = st.sidebar.text_input("Enter 6-digit Reset OTP Code", max_chars=6)
        new_password = password_input("New Password", key="new_pass")
        confirm_new_password = password_input("Confirm New Password", key="confirm_new_pass")
        
        if st.sidebar.button("Update Password", type="primary", use_container_width=True):
            if reset_otp and new_password and confirm_new_password:
                if new_password != confirm_new_password:
                    st.sidebar.error("Passwords do not match!")
                else:
                    try:
                        payload = {
                            "email": st.session_state["temp_email"],
                            "code": reset_otp,
                            "new_password": new_password
                        }
                        response = requests.post(f"{FASTAPI_URL}/auth/reset-password", json=payload)
                        
                        if response.status_code == 200:
                            st.sidebar.success("🎉 Password updated successfully! Please log in.")
                            st.session_state["auth_flow"] = "login"
                            st.session_state["temp_email"] = ""
                            st.rerun()
                        else:
                            st.sidebar.error(response.json().get("detail", "Reset failed."))
                    except Exception as e:
                        st.sidebar.error(f"Error connecting to backend: {e}")
            else:
                st.sidebar.warning("Please fill out all fields.")
                
        if st.sidebar.button("Cancel", use_container_width=True):
            st.session_state["auth_flow"] = "login"
            st.session_state["temp_email"] = ""
            st.rerun()

# If ALREADY logged in, show authenticated state
else:
    st.sidebar.success("🔑 Authenticated Successfully")
    st.sidebar.caption(f"Token: {st.session_state['token'][:20]}...") 
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["token"] = None
        st.rerun()

# ==========================================
# MAIN INTERFACE: Control Center
# ==========================================

st.title("📦 High-Scale Logistics & AI Control Center")
st.markdown("<p style='font-size: 1.1rem; opacity: 0.8; margin-top: -1.2rem; margin-bottom: 1.5rem;'>Real-time order monitoring, speed-layer caching, queue processing, and policy-aware assistant.</p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([1, 1])

# ==========================================
# COLUMN 1: Order Placement & Live Tracking
# ==========================================
with col1:
    with st.container(border=True):
        st.subheader("🛒 Order Management")
        
        # 1. Place a New Order Form
        st.markdown("#### ➕ Place a New Order")
        item_name = st.text_input("Item Name", placeholder="e.g., Gaming Laptop")
        destination = st.text_input("Destination", placeholder="e.g., New York")
        
        if st.button("Submit Order", type="primary"):
            if item_name and destination:
                if st.session_state["token"] is None:
                    st.error("Please sign in from the sidebar to submit an order.")
                else:
                    try:
                        payload = {"item_name": item_name, "destination": destination}
                        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                        response = requests.post(f"{FASTAPI_URL}/orders/", json=payload, headers=headers)

                        if response.status_code == 200:
                            st.success(f"🎉 Order placed! ID: {response.json().get('id')}")
                        else:
                            st.error(f"Failed to place order. Status Code: {response.status_code}")
                            st.json(response.json())
                    except Exception as e:
                        st.error(f"Could not connect to backend: {e}")
            else:
                st.warning("Please fill out all fields.")

        st.markdown("---")
        
        # 2. Real-Time Tracking Lookup
        st.markdown("#### ⚡ Real-Time Tracking Lookup")
        order_id = st.text_input("Enter Order ID to Track", value="1")
        
        if st.button("Fetch Tracking Status"):
            if st.session_state["token"] is None:
                st.error("Please sign in from the sidebar to fetch order tracking status.")
            else:
                try:
                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    response = requests.get(f"{FASTAPI_URL}/orders/{order_id}", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Status", data.get("status"))
                        m2.metric("Delivery Date", data.get("delivery_date") or "Calculating...")
                        
                        source = data.get("source", "Database")
                        m3.metric("Data Source", source)
                        if "Redis" in source:
                            st.info("🚀 Speed Layer Active: Fetched lightning-fast from Redis Cache!")
                        else:
                            st.warning("🏠 Cold Layer: Fetched from operational Database.")
                    else:
                        st.error(f"Order #{order_id} not found.")
                except Exception as e:
                    st.error(f"Error fetching order: {e}")

# ==========================================
# COLUMN 2: Intelligent AI Support Bot (RAG)
# ==========================================
with col2:
    with st.container(border=True):
        st.subheader("🤖 Smart AI Assistant")
        st.markdown("Ask questions about your shipments based on company policies.")
        
        bot_order_id = st.text_input("Context Order ID for Bot", value="1", key="bot_order")
        user_query = st.text_input("Ask the Bot", placeholder="When will my package arrive?")
        
        if st.button("Ask Assistant", type="secondary"):
            if user_query:
                with st.spinner("Analyzing tracking data and shipping policies..."):
                    try:
                        params = {"query": user_query, "order_id": bot_order_id}
                        response = requests.get(f"{FASTAPI_URL}/bot/ask", params=params)

                        if response.status_code == 200:
                            st.markdown("### 📝 Bot Response:")
                            st.info(response.json().get("resolved_answer"))
                        else:
                            st.error("The AI assistant encountered an issue fetching context.")
                            st.json(response.json())
                    except Exception as e:
                        st.error(f"Could not reach AI backend: {e}")