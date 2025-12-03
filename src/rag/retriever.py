"""
Document retrieval and RAG pipeline
"""
from typing import List, Dict
from src.rag.vectorstore import get_vectorstore
from src.data_loaders.custom_loader import get_data_loader
from src.config import settings


class DocumentRetriever:
    """Retrieve relevant documents for RAG"""
    
    def __init__(self):
        self.vectorstore = get_vectorstore()
        self.data_loader = get_data_loader()
    
    def retrieve_context(self, query: str, top_k: int = None) -> Dict:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
        
        Returns:
            Dictionary with retrieved documents and context
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Search vector store
        search_results = self.vectorstore.search(query, top_k=top_k)
        
        # Format results
        context = {
            'query': query,
            'documents': search_results,
            'formatted_context': self._format_context(search_results)
        }
        
        return context
    
    def _format_context(self, results: List[Dict]) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            results: List of search results
        
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        
        for i, result in enumerate(results, 1):
            doc = result['document']
            metadata = result.get('metadata', {})
            
            # Add source info if available
            source = metadata.get('source', 'Unknown')
            doc_type = metadata.get('type', 'document')
            
            context_parts.append(f"[Document {i} - {doc_type} from {source}]")
            context_parts.append(doc)
            context_parts.append("")  # Empty line
        
        return "\n".join(context_parts)
    
    def retrieve_policy_context(self, policy_type: str) -> str:
        """
        Retrieve specific policy information
        
        Args:
            policy_type: Type of policy (refund, delivery, loyalty, etc.)
        
        Returns:
            Policy content
        """
        policy = self.data_loader.get_policy(policy_type)
        
        if policy:
            content = f"**{policy['title']}**\n\n"
            content += policy['content']
            
            if 'sections' in policy:
                for section in policy['sections']:
                    content += f"\n\n**{section['heading']}**: {section['details']}"
            
            return content
        
        return f"No policy found for type: {policy_type}"
    
    def retrieve_faq_context(self, query: str) -> str:
        """
        Retrieve relevant FAQs
        
        Args:
            query: User query
        
        Returns:
            Formatted FAQs
        """
        faqs = self.data_loader.get_faq(query)
        
        if not faqs:
            return "No relevant FAQs found."
        
        faq_text = "**Relevant FAQs:**\n\n"
        
        for i, faq in enumerate(faqs[:3], 1):  # Top 3 FAQs
            faq_text += f"{i}. **Q: {faq['question']}**\n"
            faq_text += f"   A: {faq['answer']}\n\n"
        
        return faq_text
    
    def retrieve_product_context(self, category: str = None, temperature: str = None) -> str:
        """
        Retrieve product recommendations
        
        Args:
            category: Product category filter
            temperature: Temperature preference (hot/cold)
        
        Returns:
            Formatted product list
        """
        products = []
        
        if category:
            products = self.data_loader.get_products_by_category(category)
        elif temperature:
            products = self.data_loader.get_products_by_temperature(temperature)
        
        if not products:
            return "No products found matching criteria."
        
        product_text = "**Recommended Products:**\n\n"
        
        for product in products[:5]:  # Top 5 products
            product_text += f"• **{product['name']}** (₹{product['price']})\n"
            product_text += f"  {product['description']}\n"
            
            if product.get('is_seasonal'):
                product_text += "  🌟 *Seasonal Special*\n"
            
            product_text += "\n"
        
        return product_text
    
    def retrieve_promotion_context(self, category: str = None) -> str:
        """
        Retrieve active promotions
        
        Args:
            category: Product category filter
        
        Returns:
            Formatted promotions
        """
        promotions = self.data_loader.get_active_promotions(category=category)
        
        if not promotions:
            return "No active promotions at this time."
        
        promo_text = "**🎉 Active Promotions:**\n\n"
        
        for promo in promotions[:3]:  # Top 3 promotions
            promo_text += f"• **{promo['title']}**\n"
            promo_text += f"  {promo['description']}\n"
            promo_text += f"  Valid until: {promo['valid_until']}\n\n"
        
        return promo_text


def initialize_vectorstore():
    """
    Initialize vector store with documents from data files
    This should be run once to build the initial index
    """
    print("Initializing vector store...")
    
    vectorstore = get_vectorstore()
    data_loader = get_data_loader()
    
    documents = []
    metadata = []
    
    # Add policies
    for policy in data_loader.policies:
        doc_text = f"{policy['title']}\n\n{policy['content']}"
        
        if 'sections' in policy:
            for section in policy['sections']:
                doc_text += f"\n\n{section['heading']}: {section['details']}"
        
        documents.append(doc_text)
        metadata.append({
            'source': 'policies',
            'type': policy['type'],
            'title': policy['title']
        })
    
    # Add FAQs
    for faq in data_loader.faqs:
        doc_text = f"Q: {faq['question']}\nA: {faq['answer']}"
        documents.append(doc_text)
        metadata.append({
            'source': 'faqs',
            'type': faq.get('category', 'general'),
            'question': faq['question']
        })
    
    # Add product information
    for product in data_loader.products:
        doc_text = f"{product['name']}: {product['description']}"
        doc_text += f"\nCategory: {product['category']}, Price: ₹{product['price']}"
        
        documents.append(doc_text)
        metadata.append({
            'source': 'products',
            'type': 'product',
            'product_id': product['product_id'],
            'category': product['category']
        })
    
    # Create index
    if documents:
        vectorstore.create_index(documents, metadata)
        print(f"Vector store initialized with {len(documents)} documents")
        return True
    else:
        print("Warning: No documents to index")
        return False


# Global retriever instance
_retriever = None

def get_retriever() -> DocumentRetriever:
    """Get global retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = DocumentRetriever()
    return _retriever