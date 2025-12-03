import json
from typing import Dict, List, Optional
from src.config import settings


class CustomerDataLoader:
    """Load and manage customer data"""
    
    def __init__(self):
        self.customers = []
        self.products = []
        self.promotions = []
        self.locations = []
        self.policies = []
        self.faqs = []
        self.load_all_data()
    
    def load_all_data(self):
        """Load all data files"""
        self.customers = self._load_json(settings.CUSTOMERS_FILE)
        self.products = self._load_json(settings.PRODUCTS_FILE)
        self.promotions = self._load_json(settings.PROMOTIONS_FILE)
        self.locations = self._load_json(settings.LOCATIONS_FILE)
        self.policies = self._load_json(settings.POLICIES_FILE)
        self.faqs = self._load_json(settings.FAQS_FILE)
    
    @staticmethod
    def _load_json(filepath) -> List[Dict]:
        """Load JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filepath} not found")
            return []
        except json.JSONDecodeError:
            print(f"Warning: {filepath} is not valid JSON")
            return []
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict]:
        """Get customer by ID"""
        for customer in self.customers:
            if customer.get('customer_id') == customer_id:
                return customer
        return None
    
    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Alias for get_customer_by_id for agent compatibility"""
        return self.get_customer_by_id(customer_id)
    
    def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """Get customer by phone number"""
        # Normalize phone (remove spaces, dashes, etc.)
        normalized = ''.join(filter(str.isdigit, phone))
        
        for customer in self.customers:
            customer_phone = ''.join(filter(str.isdigit, customer.get('phone', '')))
            if normalized in customer_phone or customer_phone in normalized:
                return customer
        return None
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Get order details by order ID"""
        for customer in self.customers:
            for order in customer.get('order_history', []):
                if order.get('order_id') == order_id:
                    return {
                        'order': order,
                        'customer': customer
                    }
        return None
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category"""
        return [p for p in self.products if p.get('category') == category]
    
    def get_products_by_temperature(self, temp_pref: str) -> List[Dict]:
        """Get products by temperature preference (hot/cold)"""
        return [p for p in self.products if p.get('temperature') == temp_pref]
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        for product in self.products:
            if product.get('product_id') == product_id:
                return product
        return None
    
    def get_product_name(self, product_id: str) -> str:
        """Get product name by ID"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get('name', 'Unknown Product')
        return 'Unknown Product'
    
    def get_active_promotions(self, 
                             category: str = None, 
                             location_id: str = None) -> List[Dict]:
        """
        Get active promotions
        
        Args:
            category: Filter by product category
            location_id: Filter by location
        
        Returns:
            List of applicable promotions
        """
        from datetime import datetime
        
        active = []
        today = datetime.now().date()
        
        for promo in self.promotions:
            # Check date validity
            valid_from = datetime.strptime(promo['valid_from'], '%Y-%m-%d').date()
            valid_until = datetime.strptime(promo['valid_until'], '%Y-%m-%d').date()
            
            if not (valid_from <= today <= valid_until):
                continue
            
            # Check category filter
            if category:
                applicable_cats = promo.get('applicable_categories', [])
                if applicable_cats and category not in applicable_cats:
                    continue
            
            # Check location filter
            if location_id:
                store_ids = promo.get('store_ids', [])
                if store_ids and location_id not in store_ids:
                    continue
            
            active.append(promo)
        
        return active
    
    def get_customer_preferences(self, customer_id: str) -> Dict:
        """Get customer preferences"""
        customer = self.get_customer_by_id(customer_id)
        if customer:
            return customer.get('preferences', {})
        return {}
    
    def get_customer_recent_orders(self, customer_id: str, limit: int = 5) -> List[Dict]:
        """Get customer's recent orders"""
        customer = self.get_customer_by_id(customer_id)
        if customer:
            orders = customer.get('order_history', [])
            # Sort by date (most recent first)
            sorted_orders = sorted(
                orders, 
                key=lambda x: x.get('date', ''), 
                reverse=True
            )
            return sorted_orders[:limit]
        return []
    
    def search_products(self, query: str) -> List[Dict]:
        """Search products by name or description"""
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            name = product.get('name', '').lower()
            description = product.get('description', '').lower()
            
            if query_lower in name or query_lower in description:
                results.append(product)
        
        return results
    
    def get_location_by_id(self, location_id: str) -> Optional[Dict]:
        """Get location by ID"""
        for location in self.locations:
            if location.get('store_id') == location_id:
                return location
        return None
    
    def get_all_locations(self) -> List[Dict]:
        """Get all locations"""
        return self.locations
    
    def format_order_status(self, order: Dict) -> str:
        """Format order status for display"""
        status_emoji = {
            'pending': '⏳',
            'preparing': '👨‍🍳',
            'in_transit': '🚚',
            'delivered': '✅',
            'cancelled': '❌'
        }
        
        status = order.get('status', 'unknown')
        emoji = status_emoji.get(status, '📦')
        
        info = f"{emoji} Order {order.get('order_id')}\n"
        info += f"Status: {status.upper()}\n"
        info += f"Date: {order.get('date')}\n"
        info += f"Items: {', '.join(order.get('items', []))}\n"
        info += f"Total: ₹{order.get('total')}"
        
        return info
    
    def get_policy(self, policy_type: str) -> Optional[Dict]:
        """Get policy by type"""
        for policy in self.policies:
            if policy.get('type') == policy_type:
                return policy
        return None
    
    def search_policies(self, query: str) -> List[Dict]:
        """Search policies by keyword"""
        query_lower = query.lower()
        results = []
        
        for policy in self.policies:
            title = policy.get('title', '').lower()
            content = policy.get('content', '').lower()
            
            if query_lower in title or query_lower in content:
                results.append(policy)
        
        return results
    
    def get_faq(self, query: str) -> List[Dict]:
        """Search FAQs by query"""
        query_lower = query.lower()
        results = []
        
        for faq in self.faqs:
            question = faq.get('question', '').lower()
            answer = faq.get('answer', '').lower()
            
            if query_lower in question or query_lower in answer:
                results.append(faq)
        
        return results
    
    def get_all_products(self) -> List[Dict]:
        """Get all products"""
        return self.products
    
    def get_all_promotions(self) -> List[Dict]:
        """Get all active promotions"""
        return self.get_active_promotions()


# Global loader instance
_loader = None

def get_data_loader() -> CustomerDataLoader:
    """Get global data loader instance"""
    global _loader
    if _loader is None:
        _loader = CustomerDataLoader()
    return _loader