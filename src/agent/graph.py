from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import (
    retrieve_customer_info,
    check_location_context,
    retrieve_knowledge,
    generate_response
)

def build_agent_graph():
    """
    Constructs the LangGraph workflow.
    """
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("get_customer", retrieve_customer_info)
    workflow.add_node("get_location", check_location_context)
    workflow.add_node("get_knowledge", retrieve_knowledge)
    workflow.add_node("generate", generate_response)

    workflow.set_entry_point("get_customer")
    
    workflow.add_edge("get_customer", "get_location")
    workflow.add_edge("get_location", "get_knowledge")
    workflow.add_edge("get_knowledge", "generate")
    workflow.add_edge("generate", END)

    # 3. Compile
    return workflow.compile()

# Singleton instance
agent_app = build_agent_graph()