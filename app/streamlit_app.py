import streamlit as st
import sys
import os
import time
import pandas as pd

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage, AIMessage
from src.agent.graph import agent_app
from src.data_loaders.custom_loader import get_data_loader
from src.privacy.data_masking import mask_pii
from src.config.settings import settings

# Apply settings from config
st.set_page_config(
    page_title="AwareX", 
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items={"Get Help": "https://github.com", "About": "AwareX v2.0"}
)

st.markdown("""
<style>
    /* Main Background & Text */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom right, #0e1117, #161b22);
        color: #e6e6e6;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    
    /* Gradient Headers */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    /* Modern Chat Bubbles */
    .stChatMessage {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Metric Cards in Sidebar */
    div[data-testid="stMetric"] {
        background-color: #21262d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
    }
    label[data-testid="stMetricLabel"] {
        color: #8b949e;
    }
    
    /* Status Box Styling */
    .stStatus {
        background-color: #1f2937 !important;
        border: 1px solid #10b981 !important;
        color: #a7f3d0 !important;
        border-radius: 8px;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #21262d;
        border-radius: 8px;
        color: #c9d1d9;
    }
    
    /* Custom Badge for Preferences */
    .pref-badge {
        background-color: #238636;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Load Data
loader = get_data_loader()
customers = loader.customers

def stream_text(text):
    for char in text.split(" "):
        yield char + " "
        time.sleep(0.015) # Slightly faster for modern feel

with st.sidebar:
    st.title("Simulation")
    
    # User Selector
    customer_names = {c['customer_id']: c['name'] for c in customers}
    selected_user_id = st.selectbox(
        "Select Persona",
        options=list(customer_names.keys()),
        format_func=lambda x: customer_names[x]
    )
    
    current_user = loader.get_customer(selected_user_id)
    
    st.markdown("---")
    
    # Profile Card
    st.markdown(f"### 👤 {current_user['name']}")
    st.caption(f"📍 {current_user['location']['city']}")
    
    # Metrics row
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Loyalty Tier", "🥇 Gold" if current_user['loyalty_points'] > 500 else "🥈 Silver")
    with col2:
        st.metric("Points", current_user['loyalty_points'])
    
    st.markdown("---")
    
    # Preferences with custom badges
    st.markdown("**❤️ Preferences**")
    for prod_id in current_user['preferences']['favorite_products']:
        prod_name = loader.get_product_name(prod_id)
        st.markdown(f'<span class="pref-badge">{prod_name}</span>', unsafe_allow_html=True)
    
    # Privacy Toggle
    st.markdown("---")
    default_privacy = settings.ENABLE_PII_MASKING
    enable_privacy = st.toggle("🛡️ Privacy Shield", value=default_privacy, help="Enable PII masking before sending to AI")

c1, c2 = st.columns([0.8, 0.2])
with c1:
    st.title("AwareX")
    st.markdown(f"**Hyper-Personalized Customer Experience** | Context: `{current_user['location']['city']}`")

st.markdown("---")

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_user" not in st.session_state:
    st.session_state.last_user = selected_user_id

# Clear chat if user changes
if st.session_state.last_user != selected_user_id:
    st.session_state.messages = []
    st.session_state.last_user = selected_user_id

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg.content)

st.markdown("---")

# Chat Input
user_input = st.chat_input("💬 How can I help you today?")

if user_input:
    # Display User Message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
    st.session_state.messages.append(HumanMessage(content=user_input))

    # Privacy Check
    processed_input = user_input
    if enable_privacy:
        processed_input = mask_pii(user_input)
        if processed_input != user_input:
            with st.status("🛡️ Privacy Shield Active"):
                st.write(f"**Original:** {user_input}")
                st.write(f"**Masked sent to LLM:** {processed_input}")

    # Run Agent
    with st.spinner("Thinking..."):
        try:
            # Prepare inputs for the graph
            graph_inputs = {
                "user_id": selected_user_id,
                "messages": st.session_state.messages,
                "intent": "general"
            }
            
            # Invoke Graph
            result = agent_app.invoke(graph_inputs)
            ai_response = result["final_response"]
            
        except Exception as e:
            ai_response = f"⚠️ Error: {str(e)}"
            result = {}

    # streaming
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Simulate typing effect
        for chunk in stream_text(ai_response):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
        
    st.session_state.messages.append(AIMessage(content=ai_response))

    with st.expander("🧠 View Agent Reasoning & Retrieved Context"):
        c1, c2 = st.columns(2)
        
        # Location Context & Map
        with c1:
            st.markdown("**📍 Location Logic:**")
            loc_ctx = result.get('location_context', {})
            st.json(loc_ctx)
            
            # MAP VISUALIZATION
            if 'store_lat' in loc_ctx:
                st.markdown("### 🗺️ Live Context Map")
                
                # User Coords
                u_lat = current_user['location']['latitude']
                u_lon = current_user['location']['longitude']
                
                # Store Coords
                s_lat = loc_ctx['store_lat']
                s_lon = loc_ctx['store_lon']
                
                # Create DataFrame for Map
                map_data = pd.DataFrame({
                    'lat': [u_lat, s_lat],
                    'lon': [u_lon, s_lon],
                })
                
                # Display map
                st.map(map_data, height=300 ,zoom=20)

        # RAG Context
        with c2:
            st.markdown("**📚 RAG Knowledge Base:**")
            st.caption(result.get('rag_context', 'No context retrieved')[:500] + "...")
            
            # Order Context if available
            order_ctx = result.get('order_context', '')
            if order_ctx:
                st.markdown("**📦 Order Details Injected:**")
                st.info(order_ctx)