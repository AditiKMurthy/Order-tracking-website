import streamlit as st
import requests
import os

# Configure the page title and layout
st.set_page_config(page_title="Logistics Control Center", layout="wide")

# Get FastAPI backend URL dynamically from cloud environment variables
# Falls back to localhost automatically for local development testing
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@omnistream.com")

# ==========================================
# SIDEBAR: User Authentication & Registration
# ==========================================
st.sidebar.header("🔐 User Authentication")

if "token" not in st.session_state:
    st.session_state["token"] = None

# If NOT logged in, show Login and Register tabs
if st.session_state["token"] is None:
    # Create two clean functional tabs in the sidebar
    auth_tab, register_tab = st.sidebar.tabs(["Login", "Register"])
    
    # ------------------
    # TAB 1: LOGIN
    # ------------------
    with auth_tab:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
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
                        st.error("Invalid credentials.")
                except Exception as e:
                    st.error(f"Auth Backend unreachable: {e}")
            else:
                st.warning("Please fill out all fields.")

    # ------------------
    # TAB 2: REGISTER
    # ------------------
    with register_tab:
        new_username = st.text_input("Choose Username", key="reg_user")
        new_password = st.text_input("Choose Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_pass_conf")
        
        if st.button("Create Account", type="secondary", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    try:
                        # Send as raw JSON payload to match UserCreate schema
                        register_payload = {"username": new_username, "password": new_password}
                        response = requests.post(f"{FASTAPI_URL}/auth/register", json=register_payload)
                        
                        if response.status_code == 201:
                            st.success("🎉 Account created! You can now log in.")
                        else:
                            err_detail = response.json().get("detail", "Registration failed.")
                            st.error(f"Error: {err_detail}")
                    except Exception as e:
                        st.error(f"Auth Backend unreachable: {e}")
            else:
                st.warning("Please fill out all fields.")

# If ALREADY logged in, hide input text fields and display active state
else:
    st.sidebar.success("🔑 Authenticated Successfully")
    st.sidebar.caption(f"Token active: {st.session_state['token'][:15]}...") 
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["token"] = None
        st.rerun()

# ==========================================
# MAIN INTERFACE: Control Center
# ==========================================

st.title("📦 High-Scale Logistics & AI Control Center")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# ==========================================
# COLUMN 1: Order Placement & Live Tracking
# ==========================================
with col1:
    st.header("🛒 Order Management")
    
    # 1. Place a New Order Form
    with st.expander("➕ Place a New Order", expanded=True):
        item_name = st.text_input("Item Name", placeholder="e.g., Gaming Laptop")
        destination = st.text_input("Destination", placeholder="e.g., New York")
        
        if st.button("Submit Order", type="primary"):
            if item_name and destination:
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

    # 2. Real-Time Tracking Lookup
    st.markdown("---")
    st.header("⚡ Real-Time Tracking Lookup")
    order_id = st.text_input("Enter Order ID to Track", value="1")
    
    if st.button("Fetch Tracking Status"):
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
                    st.warning("🏠 Cold Layer: Fetched from PostgreSQL Database.")
            else:
                st.error(f"Order #{order_id} not found.")
        except Exception as e:
            st.error(f"Error fetching order: {e}")

# ==========================================
# COLUMN 2: Intelligent AI Support Bot (RAG)
# ==========================================
with col2:
    st.header("🤖 Smart AI Assistant")
    st.write("Ask questions about your shipments based on company policies.")
    
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