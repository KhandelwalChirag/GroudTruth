import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage, AIMessage
from src.agent.graph import agent_app
from src.data_loaders.custom_loader import get_data_loader
from src.privacy.data_masking import mask_pii

# Page Config
st.set_page_config(page_title="AwareX", layout="wide")

# Load Data
loader = get_data_loader()
customers = loader.customers

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("⚙️ Simulation Controls")
    
    # User Selector
    customer_names = {c['customer_id']: c['name'] for c in customers}
    selected_user_id = st.selectbox(
        "Select Active Customer",
        options=list(customer_names.keys()),
        format_func=lambda x: customer_names[x]
    )
    
    current_user = loader.get_customer(selected_user_id)
    
    # Display Customer Context
    st.divider()
    st.subheader("👤 User Profile")
    st.markdown(f"**Name:** {current_user['name']}")
    st.markdown(f"**Location:** {current_user['location']['city']}")
    st.markdown(f"**Loyalty Tier:** {'🥇 Gold' if current_user['loyalty_points'] > 500 else '🥈 Silver'}")
    st.markdown(f"**Points:** {current_user['loyalty_points']}")
    
    # Preferences
    st.info(f"❤️ Loves: {', '.join([loader.get_product_name(pid) for pid in current_user['preferences']['favorite_products']])}")
    
    # Privacy Toggle
    st.divider()
    enable_privacy = st.toggle("🛡️ Enable Privacy Mode (PII Masking)", value=True)

# --- MAIN CHAT INTERFACE ---
st.title("AwareX: Hyper-Personalized Agent")
st.markdown(f"Acting as **{current_user['name']}** in **{current_user['location']['city']}**")

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
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Chat Input
user_input = st.chat_input("How can I help you today?")

if user_input:
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append(HumanMessage(content=user_input))

    # 2. Privacy Check
    processed_input = user_input
    if enable_privacy:
        processed_input = mask_pii(user_input)
        if processed_input != user_input:
            with st.status("🛡️ Privacy Shield Active"):
                st.write(f"**Original:** {user_input}")
                st.write(f"**Masked sent to LLM:** {processed_input}")

    # 3. Run Agent
    with st.spinner("Thinking..."):
        try:
            # Prepare inputs for the graph
            graph_inputs = {
                "user_id": selected_user_id,
                "messages": st.session_state.messages,
                "intent": "general" # Can be updated by parser in future
            }
            
            # Invoke Graph
            result = agent_app.invoke(graph_inputs)
            ai_response = result["final_response"]
            
            # Show "Under the Hood" Context
            with st.expander("🧠 View Agent Reasoning & Retrieved Context"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**📍 Location Logic:**")
                    loc_ctx = result.get('location_context', {})
                    st.json(loc_ctx)
                with c2:
                    st.markdown("**📚 RAG Knowledge Base:**")
                    st.caption(result.get('rag_context', 'No context retrieved')[:500] + "...")

        except Exception as e:
            ai_response = f"⚠️ Error: {str(e)}"

    # 4. Display AI Response
    with st.chat_message("assistant"):
        st.markdown(ai_response)
    st.session_state.messages.append(AIMessage(content=ai_response))