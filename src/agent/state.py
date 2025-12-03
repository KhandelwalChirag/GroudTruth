import operator
from typing import Annotated, TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    The state of the agent execution.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    
    # Retrieved Context Data
    user_info: Dict[str, Any]      
    location_context: Dict[str, Any]
    rag_context: str
    order_context: str               
    
    intent: str
    
    final_response: str