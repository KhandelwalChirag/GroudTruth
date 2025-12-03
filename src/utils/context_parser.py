"""
Context parsing utilities to extract intent and entities from user messages
"""
from typing import Dict, List, Optional
import re


class ContextParser:
    """Parse user messages to extract intent and context"""
    
    # Intent patterns
    INTENT_PATTERNS = {
        'order_status': [
            r'\bwhere\s+is\s+my\s+order\b',
            r'\border\s+status\b',
            r'\btrack\s+order\b',
            r'\bmy\s+order\b',
        ],
        'refund_request': [
            r'\brefund\b',
            r'\bmoney\s+back\b',
            r'\breturn\b',
            r'\bcancel\s+order\b',
        ],
        'location_query': [
            r'\bnear\s+me\b',
            r'\bnearest\s+store\b',
            r'\bwhere\s+can\s+i\b',
            r'\bhow\s+far\b',
            r'\bclose\s+by\b',
        ],
        'product_recommendation': [
            r'\bwhat\s+should\s+i\b',
            r'\brecommend\b',
            r'\bsuggest\b',
            r'\bi\s+want\s+something\b',
        ],
        'temperature_related': [
            r'\bi\'?m\s+(cold|hot|warm|freezing)\b',
            r'\bfeeling\s+(cold|hot|warm|chilly)\b',
            r'\bweather\s+is\s+(cold|hot)\b',
        ],
        'complaint': [
            r'\bcomplain\b',
            r'\bnot\s+happy\b',
            r'\bdissatisfied\b',
            r'\bwrong\s+order\b',
            r'\bcold\s+coffee\b',
        ],
    }
    
    # Entity patterns
    TEMPERATURE_KEYWORDS = {
        'cold': ['cold', 'freezing', 'chilly', 'freeze', 'frozen'],
        'hot': ['hot', 'warm', 'heat', 'burning'],
    }
    
    PRODUCT_CATEGORIES = {
        'hot_beverage': ['coffee', 'tea', 'latte', 'cappuccino', 'hot chocolate', 'espresso'],
        'cold_beverage': ['iced', 'cold brew', 'smoothie', 'frappe', 'shake'],
        'food': ['sandwich', 'pastry', 'muffin', 'croissant', 'cake', 'salad'],
    }
    
    @staticmethod
    def detect_intent(message: str) -> List[str]:
        """
        Detect user intent from message
        
        Args:
            message: User's message
        
        Returns:
            List of detected intents
        """
        message_lower = message.lower()
        detected_intents = []
        
        for intent, patterns in ContextParser.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected_intents.append(intent)
                    break
        
        return detected_intents if detected_intents else ['general_query']
    
    @staticmethod
    def extract_temperature_context(message: str) -> Optional[str]:
        """
        Extract temperature-related context (hot/cold)
        
        Args:
            message: User's message
        
        Returns:
            'hot', 'cold', or None
        """
        message_lower = message.lower()
        
        for temp_type, keywords in ContextParser.TEMPERATURE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return temp_type
        
        return None
    
    @staticmethod
    def extract_product_preferences(message: str) -> List[str]:
        """
        Extract product category preferences from message
        
        Args:
            message: User's message
        
        Returns:
            List of relevant product categories
        """
        message_lower = message.lower()
        preferences = []
        
        for category, keywords in ContextParser.PRODUCT_CATEGORIES.items():
            for keyword in keywords:
                if keyword in message_lower:
                    if category not in preferences:
                        preferences.append(category)
                    break
        
        return preferences
    
    @staticmethod
    def extract_order_id(message: str) -> Optional[str]:
        """
        Extract order ID from message
        
        Args:
            message: User's message
        
        Returns:
            Order ID or None
        """
        # Match patterns like ORD1001, ORDER123, #12345
        patterns = [
            r'\bORD\d+\b',
            r'\bORDER\d+\b',
            r'#\d+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.upper())
            if match:
                return match.group(0).lstrip('#')
        
        return None
    
    @staticmethod
    def is_urgent(message: str) -> bool:
        """
        Detect if message indicates urgency
        
        Args:
            message: User's message
        
        Returns:
            True if urgent
        """
        urgent_keywords = [
            'urgent', 'asap', 'emergency', 'immediately', 'right now',
            'hurry', 'quick', 'fast', 'waiting', 'late'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in urgent_keywords)
    
    @staticmethod
    def parse_context(message: str, customer_data: Optional[Dict] = None) -> Dict:
        """
        Parse complete context from message
        
        Args:
            message: User's message
            customer_data: Optional customer information
        
        Returns:
            Dictionary with parsed context
        """
        context = {
            'message': message,
            'intents': ContextParser.detect_intent(message),
            'temperature_context': ContextParser.extract_temperature_context(message),
            'product_preferences': ContextParser.extract_product_preferences(message),
            'order_id': ContextParser.extract_order_id(message),
            'is_urgent': ContextParser.is_urgent(message),
            'customer_data': customer_data,
        }
        
        return context
    
    @staticmethod
    def format_context_summary(context: Dict) -> str:
        """
        Format context for display/debugging
        
        Args:
            context: Parsed context dictionary
        
        Returns:
            Formatted string
        """
        lines = [
            f"Intents: {', '.join(context['intents'])}",
        ]
        
        if context['temperature_context']:
            lines.append(f"Temperature: {context['temperature_context']}")
        
        if context['product_preferences']:
            lines.append(f"Products: {', '.join(context['product_preferences'])}")
        
        if context['order_id']:
            lines.append(f"Order ID: {context['order_id']}")
        
        if context['is_urgent']:
            lines.append("⚠️ URGENT")
        
        return '\n'.join(lines)