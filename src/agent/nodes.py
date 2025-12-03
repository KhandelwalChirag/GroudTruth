from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

from src.config import settings
from src.agent.state import AgentState
from src.agent.prompts import get_chat_prompt
from src.data_loaders.custom_loader import get_data_loader
from src.utils.location_utils import find_nearby_locations
from src.rag.retriever import get_retriever

# Initialize Global Tools
loader = get_data_loader()
retriever = get_retriever()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.7
)

# Helper function to format order history
def _format_order_history(orders: list, data_loader) -> str:
    """Format order history for context injection"""
    if not orders:
        return ""
    
    order_text = "**Customer Order History:**\n\n"
    
    for order in orders:
        order_id = order.get("order_id", "N/A")
        status = order.get("status", "Unknown")
        date = order.get("date", "N/A")
        items = order.get("items", [])
        total = order.get("total", "N/A")
        
        # Get product names
        item_names = [data_loader.get_product_name(item_id) for item_id in items]
        
        order_text += f"📦 Order ID: {order_id}\n"
        order_text += f"   Status: {status.upper()}\n"
        order_text += f"   Date: {date}\n"
        order_text += f"   Items: {', '.join(item_names)}\n"
        order_text += f"   Total: ₹{total}\n\n"
    
    return order_text

def retrieve_customer_info(state: AgentState):
    """Node: Fetch customer profile based on ID."""
    user_id = state.get("user_id")
    customer = loader.get_customer(user_id)
    
    if not customer:
        return {"user_info": {"name": "Guest", "loyalty_points": 0, "preferences": {}, "location": {}}}
    
    # Ensure customer has required fields for downstream processing
    if "location" not in customer:
        customer["location"] = {}
        
    return {"user_info": customer}

def check_location_context(state: AgentState):
    """Node: Find nearest stores based on customer location."""
    user_info = state.get("user_info", {})
    cust_loc = user_info.get("location", {})
    
    # Handle missing location data
    if not cust_loc or not cust_loc.get("latitude") or not cust_loc.get("longitude"):
        return {"location_context": {
            "nearest_store": "Unknown",
            "distance": "N/A",
            "city": "Unknown"
        }}
    
    try:
        # Find nearest stores
        nearby = find_nearby_locations(
            user_lat=cust_loc.get("latitude"),
            user_lon=cust_loc.get("longitude"),
            max_distance_km=50
        )
        
        if nearby:
            store = nearby[0]
            context = {
                "nearest_store": store.get('name', 'Unknown'),
                "distance": round(store.get('distance_km', 0), 2),
                "city": cust_loc.get("city", "Unknown")
            }
        else:
            context = {
                "nearest_store": "None found nearby",
                "distance": "N/A",
                "city": cust_loc.get("city", "Unknown")
            }
    except Exception as e:
        print(f"Error finding nearby locations: {e}")
        context = {
            "nearest_store": "Unknown",
            "distance": "N/A",
            "city": cust_loc.get("city", "Unknown")
        }
        
    return {"location_context": context}

def retrieve_knowledge(state: AgentState):
    """Node: RAG Retrieval based on the latest user message."""
    messages = state.get("messages", [])
    user_info = state.get("user_info", {})
    
    if not messages:
        return {"rag_context": "", "order_context": ""}
    
    # Get last user message
    last_message = messages[-1].content
    last_message_lower = last_message.lower()
    
    # Check if query is about orders/tracking
    order_keywords = ["order", "track", "where is", "status", "deliver", "shipped", "transit"]
    is_order_query = any(keyword in last_message_lower for keyword in order_keywords)
    
    order_context = ""
    if is_order_query and user_info.get("order_history"):
        # Extract order information for order-related queries
        orders = user_info.get("order_history", [])
        if orders:
            order_context = _format_order_history(orders, loader)
    
    # Retrieve docs from RAG
    result = retriever.retrieve_context(last_message)
    rag_context = result["formatted_context"]
    
    return {"rag_context": rag_context, "order_context": order_context}

def generate_response(state: AgentState):
    """Node: Call Gemini to generate the final answer."""
    user_info = state.get("user_info", {})
    loc_ctx = state.get("location_context", {})
    rag_ctx = state.get("rag_context", "")
    order_ctx = state.get("order_context", "")
    messages = state.get("messages", [])
    
    # Combine order context with RAG context
    combined_context = rag_ctx
    if order_ctx:
        combined_context = order_ctx + "\n\n" + rag_ctx
    
    # Prepare Prompt Inputs
    prompt_inputs = {
        "user_name": user_info.get("name", "Guest"),
        "loyalty_points": user_info.get("loyalty_points", 0),
        "preferences": str(user_info.get("preferences", {})),
        "current_location": user_info.get("location", {}).get("address", "Unknown"),
        "nearest_store": loc_ctx.get("nearest_store", "Unknown"),
        "distance": loc_ctx.get("distance", "N/A"),
        "rag_context": combined_context,
        "messages": messages
    }
    
    try:
        # Generate
        chain = get_chat_prompt() | llm
        response = chain.invoke(prompt_inputs)
        
        # Create response object
        ai_response = AIMessage(content=response.content)
        
        return {
            "final_response": response.content,
            "messages": [ai_response]  # Return as list for operator.add to work
        }
    except Exception as e:
        print(f"Error generating response: {e}")
        error_response = AIMessage(content="I apologize, but I encountered an error processing your request. Please try again.")
        return {
            "final_response": "Error",
            "messages": [error_response]
        }