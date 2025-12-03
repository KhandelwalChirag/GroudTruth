"""
PII (Personally Identifiable Information) masking utilities
Ensures customer privacy by redacting sensitive data before sending to LLM
"""
import re
from typing import Dict, List, Tuple


class PIIMasker:
    """Mask personally identifiable information"""
    
    # Regex patterns for PII detection
    PATTERNS = {
        'phone': [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
            r'\+91[-.\s]?\d{10}',  # Indian
            r'\d{10}',  # Simple 10-digit
        ],
        'email': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        'credit_card': [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        ],
        'ip_address': [
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        ],
    }
    
    # Replacement tokens
    MASKS = {
        'phone': '[PHONE_REDACTED]',
        'email': '[EMAIL_REDACTED]',
        'credit_card': '[CARD_REDACTED]',
        'ip_address': '[IP_REDACTED]',
    }
    
    @staticmethod
    def mask_text(text: str, entities: List[str] = None) -> Tuple[str, List[Dict]]:
        """
        Mask PII in text
        
        Args:
            text: Text to mask
            entities: List of entity types to mask (if None, mask all)
        
        Returns:
            Tuple of (masked_text, list of detected entities)
        """
        if entities is None:
            entities = list(PIIMasker.PATTERNS.keys())
        
        masked_text = text
        detected = []
        
        for entity_type in entities:
            if entity_type not in PIIMasker.PATTERNS:
                continue
            
            for pattern in PIIMasker.PATTERNS[entity_type]:
                matches = re.finditer(pattern, masked_text)
                for match in matches:
                    original = match.group(0)
                    detected.append({
                        'type': entity_type,
                        'original': original,
                        'start': match.start(),
                        'end': match.end()
                    })
                    masked_text = masked_text.replace(
                        original, 
                        PIIMasker.MASKS[entity_type]
                    )
        
        return masked_text, detected
    
    @staticmethod
    def mask_customer_data(customer: Dict) -> Dict:
        """
        Mask PII in customer data dictionary
        
        Args:
            customer: Customer data dictionary
        
        Returns:
            Customer data with PII masked
        """
        masked = customer.copy()
        
        # Mask phone
        if 'phone' in masked:
            masked['phone'] = PIIMasker.MASKS['phone']
        
        # Mask email
        if 'email' in masked:
            masked['email'] = PIIMasker.MASKS['email']
        
        # Keep first name only
        if 'name' in masked:
            parts = masked['name'].split()
            masked['name'] = parts[0] + ' [LAST_NAME_REDACTED]'
        
        # Mask order history payment details (if any)
        if 'order_history' in masked:
            for order in masked['order_history']:
                if 'payment_method' in order:
                    order['payment_method'] = '[PAYMENT_REDACTED]'
        
        return masked
    
    @staticmethod
    def create_safe_context(customer: Dict, include_fields: List[str] = None) -> Dict:
        """
        Create a safe context with only necessary customer info
        
        Args:
            customer: Full customer data
            include_fields: List of fields to include
        
        Returns:
            Safe customer context
        """
        if include_fields is None:
            include_fields = [
                'customer_id', 
                'preferences', 
                'loyalty_points',
                'order_history'
            ]
        
        safe_context = {}
        
        for field in include_fields:
            if field in customer:
                safe_context[field] = customer[field]
        
        # Add masked name (first name only)
        if 'name' in customer:
            parts = customer['name'].split()
            safe_context['first_name'] = parts[0]
        
        # Add general location (city only, no exact coordinates)
        if 'location' in customer and 'city' in customer['location']:
            safe_context['city'] = customer['location']['city']
        
        return safe_context
    
    @staticmethod
    def unmask_for_display(masked_text: str, original_data: Dict) -> str:
        """
        Unmask data for display to customer (reverse operation)
        
        Args:
            masked_text: Text with masks
            original_data: Original data before masking
        
        Returns:
            Text with masks replaced by partial info (e.g., ***-1234 for phone)
        """
        unmasked = masked_text
        
        # Show last 4 digits of phone
        if 'phone' in original_data:
            phone = original_data['phone']
            last_4 = phone[-4:] if len(phone) >= 4 else phone
            unmasked = unmasked.replace(
                PIIMasker.MASKS['phone'],
                f'***-{last_4}'
            )
        
        # Show partial email
        if 'email' in original_data:
            email = original_data['email']
            parts = email.split('@')
            if len(parts) == 2:
                partial = f"{parts[0][:2]}***@{parts[1]}"
                unmasked = unmasked.replace(
                    PIIMasker.MASKS['email'],
                    partial
                )
        
        return unmasked
    
    @staticmethod
    def validate_privacy_compliance(text: str) -> Tuple[bool, List[str]]:
        """
        Check if text contains unmasked PII
        
        Args:
            text: Text to validate
        
        Returns:
            Tuple of (is_compliant, list of issues)
        """
        issues = []
        
        for entity_type, patterns in PIIMasker.PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    issues.append(
                        f"Unmasked {entity_type} found: {len(matches)} instance(s)"
                    )
        
        is_compliant = len(issues) == 0
        return is_compliant, issues


# Convenience functions
def mask_pii(text: str) -> str:
    """Quick function to mask all PII in text"""
    masked, _ = PIIMasker.mask_text(text)
    return masked


def create_safe_customer_context(customer: Dict) -> Dict:
    """Quick function to create safe customer context"""
    return PIIMasker.create_safe_context(customer)