# ☕ GroudTruth | Hyper-Personalized Customer Support Agent MVP

> **AwareX**: Context-Aware Customer Experience Automation  
> Built with LangGraph, RAG (FAISS), Gemini API, and Streamlit

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1.0-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)
![Google Gemini](https://img.shields.io/badge/Gemini%20API-Latest-yellow.svg)

---

## 🎯 Problem Statement

**Challenge**: Retail customers expect instant, contextual answers without explicitly providing all details (location, preferences, history).

**Solution**: An AI agent that automatically interprets vague customer inputs using location data, purchase history, preferences, and real-time context to provide hyper-personalized, actionable support.

### Example Interaction
```
User: "I'm cold"
Agent: "Great! There's a Brew & Bite café 50m away in Connaught Place. 
        Since you love hot beverages, we have a 10% coupon on our 
        Masala Chai today. Your loyalty points: 250 🎟️"
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
# Clone repository
git clone https://github.com/KhandelwalChirag/GroudTruth.git
cd GroudTruth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your keys:
GOOGLE_API_KEY=your-gemini-api-key-here
```

### 3. Run the Application
```bash
# Start Streamlit app
streamlit run app/streamlit_app.py
```

🎉 **Done!** Open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
GroudTruth/
├── README.md
├── requirements.txt
├── .env.example
├── test_config.py
│
├── data/                              # Sample Data
│   ├── customers.json                 # Customer profiles & history
│   ├── locations.json                 # Store/business locations
│   ├── products.json                  # Product catalog
│   ├── promotions.json                # Active promotions/coupons
│   ├── faqs.json                      # FAQ database
│   ├── policies.json                  # Company policies
│   └── vectorstore/
│       └── customer_support_index.index  # FAISS vector index
│
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                # API keys, paths, global config
│   │
│   ├── data_loaders/
│   │   ├── __init__.py
│   │   └── custom_loader.py           # Data loading & querying
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py              # Gemini embeddings wrapper
│   │   ├── retriever.py               # RAG retrieval logic
│   │   └── vectorstore.py             # FAISS vector store setup
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                   # LangGraph workflow definition
│   │   ├── nodes.py                   # Workflow nodes/steps
│   │   ├── state.py                   # Agent state schema
│   │   └── prompts.py                 # System prompts
│   │
│   ├── privacy/
│   │   ├── __init__.py
│   │   └── data_masking.py            # PII redaction (phone, email)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── context_parser.py          # Intent & context analysis
│       └── location_utils.py          # Geolocation & distance calcs
│
├── app/
│   ├── __init__.py
│   └── streamlit_app.py               # UI & chat interface
│
└── tests/
    └── __init__.py
```

---

## 🛠️ Technical Architecture

### Agent Workflow (LangGraph)
```
┌─────────────────┐
│  User Input     │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │ 1. Get Customer Info │  (Fetch profile, preferences, history)
    └────┬─────────────────┘
         │
    ┌────▼──────────────────────┐
    │ 2. Check Location Context │  (Find nearest stores, distance)
    └────┬──────────────────────┘
         │
    ┌────▼────────────────────┐
    │ 3. Retrieve Knowledge   │  (RAG: Policies, FAQs, Promotions)
    └────┬────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │ 4. Generate Response (Gemini) │  (Synthesize answer with context)
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────┐
    │ Final Response    │
    └───────────────────┘
```

### RAG Pipeline
```
Documents (Policies, FAQs, Products)
         ↓
    Gemini Embeddings (768-dim normalized)
         ↓
    FAISS Vector Store
         ↓
    Similarity Search
         ↓
    Retrieved Context + LLM Prompt
```

### Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Google Gemini 2.5-Flash | Response generation |
| **Embeddings** | Gemini Embedding 001 | Vector representations (RAG) |
| **Vector Store** | FAISS | Fast similarity search |
| **Graph Framework** | LangGraph | Workflow orchestration |
| **UI Framework** | Streamlit | Interactive chat interface |
| **PII Protection** | Regex-based masking | Privacy enforcement |
| **Location** | Haversine formula | Distance calculations |

---

## 🎬 Demo Scenarios

### Scenario 1: Context-Aware Recommendation (Weather-Based)
**User Context**: Priya Sharma @ Connaught Place, Delhi | Preferences: Hot drinks, Vegetarian

```
User: "I'm cold"

Agent Reasoning:
  ✓ Location: Connaught Place (28.6139°N, 77.2090°E)
  ✓ Finds: Connaught Place Flagship (0.0 km away)
  ✓ Preferences: Hot drinks, Vegetarian
  ✓ Suggests: Masala Chai, Vegetarian Samosa
  ✓ Active Promo: 10% off Hot Beverages
  ✓ Loyalty: 250 points → Silver tier

Response: "Looks like you need warmth! ☕ Our Connaught Place 
           Flagship is just steps away. Try our Masala Chai with 
           a Fresh Samosa - 10% off today for you!"
```

### Scenario 2: Order Tracking
**User Context**: Rahul Verma @ Gurgaon | Order Status: In Transit

```
User: "Where's my order?"

Agent Reasoning:
  ✓ Retrieves: Order ORD1002 (Dec 3, 2024)
  ✓ Items: Iced Coffee, Energy Bar
  ✓ Status: In Transit
  ✓ Store: Cyber Hub Social
  ✓ Loyalty: 500 points → Gold tier

Response: "Your order is on the way! 🚚 
          Expected: Dec 3, 2024 (5 mins) 
          Items: Iced Coffee x1, Energy Bar x1 
          Total: ₹480"
```

### Scenario 3: Policy Inquiry
```
User: "What's your return policy?"

Agent Reasoning:
  ✓ Searches RAG index for "return policy"
  ✓ Retrieves policy document
  ✓ Extracts relevant sections

Response: "We offer 30-day returns on all items. 
          Conditions: Original packaging, receipt required. 
          Refund: Full amount to original payment method."
```

### Scenario 4: Personalized Suggestion
```
User: "What should I order?"

Agent Reasoning:
  ✓ Analyzes: Purchase history (5 recent orders)
  ✓ Products: Iced Coffee (most frequent)
  ✓ Checks: Similar items in catalog
  ✓ Applies: Promotions on items you like

Response: "Based on your history, try our Cold Brew Latte! 
          You loved our Iced Coffee last week. 
          Today's offer: Free upgrade to Large (50% off)."
```

---

## 🔒 Privacy & Security

### PII Masking
All sensitive information is redacted before sending to LLM:

```python
# Input
"Call me at +91-9876543210 or priya.sharma@email.com"

# After Masking
"Call me at +91-XXXX43210 or p*****@email.com"

# What's Protected
✅ Phone numbers      ✅ Email addresses
✅ Full names         ✅ Tracking IDs (contextually)
✅ Addresses          ✅ Financial info
```

### Debug Mode
Streamlit UI includes a "Privacy Mode" toggle to see:
- Original vs. masked input
- Raw prompt sent to LLM
- Retrieved context
- Reasoning chain

---

### Enhanced Features (Phase 2) 🚧
- [ ] Multi-turn conversation memory
- [ ] Sentiment analysis
- [ ] Voice input/output
- [ ] Advanced intent classification (NLU)
- [ ] A/B testing framework
- [ ] Response quality metrics

### Production Ready (Phase 3) 🔮
- [ ] Real database integration
- [ ] Authentication & authorization
- [ ] Comprehensive logging & monitoring
- [ ] Unit & integration tests
- [ ] API endpoints
- [ ] Scalable deployment (Docker, K8s)

---

## 🧪 Testing & Validation

### Manual Test Cases

1. **Location & Weather Test**
   ```
   Customer: Priya Sharma (Cold preference)
   Input: "I'm cold"
   Expected: Hot beverage suggestion + nearest store
   ```

2. **Order Status Test**
   ```
   Customer: Rahul Verma (Active order)
   Input: "Where's my order?"
   Expected: Order details + tracking info
   ```

3. **Policy Test**
   ```
   Input: "Can I return this?"
   Expected: Return policy from RAG
   ```

4. **Privacy Test**
   ```
   Enable Privacy Mode
   Input: "My number is 555-0123"
   Expected: Masked before LLM
   ```


## 🚧 Known Limitations

1. **Sample Data Only**: Uses JSON files (connect to real DB in production)
2. **Single Turn**: No multi-turn conversation memory
3. **Intent Detection**: Keyword-based (upgrade to NLU model)
4. **Basic RAG**: Simple cosine similarity (add re-ranking, hybrid search)
5. **Embedding Normalization**: Optimized for 768-dim (adjust for production)
6. **Geolocation**: Fixed user locations (add dynamic geocoding)

---

## 🔮 Future Enhancements

### Short-term
- [ ] Add conversation memory (storing context between turns)
- [ ] Implement NER (Named Entity Recognition) for better context
- [ ] Add product recommendation engine
- [ ] Sentiment analysis for customer satisfaction

### Mid-term
- [ ] Connect to real database (PostgreSQL, MongoDB)
- [ ] Add voice capabilities (speech-to-text, text-to-speech)
- [ ] Multi-language support (Hindi, other regional languages)
- [ ] CRM integration (Salesforce, HubSpot)

### Long-term 
- [ ] Reinforcement learning from human feedback
- [ ] Custom fine-tuned embeddings
- [ ] Edge deployment for offline mode
- [ ] Analytics & insights dashboard
- [ ] Proactive notifications system

---

## 📚 Code Examples

### Using the Data Loader
```python
from src.data_loaders.custom_loader import get_data_loader

loader = get_data_loader()

# Get customer info
customer = loader.get_customer("CUST001")

# Get nearby locations
nearby = loader.get_all_locations()

# Find product name
product_name = loader.get_product_name("PROD001")

# Get active promotions
promos = loader.get_active_promotions(category="Hot Drinks")

# Search FAQs
faqs = loader.get_faq("return policy")
```

### Using the Agent
```python
from src.agent.graph import agent_app
from langchain_core.messages import HumanMessage

# Prepare input
graph_inputs = {
    "user_id": "CUST001",
    "messages": [HumanMessage(content="I'm cold")],
    "intent": "general"
}

# Run agent
result = agent_app.invoke(graph_inputs)
print(result["final_response"])
```

### PII Masking
```python
from src.privacy.data_masking import mask_pii

text = "Call me at +91-9876543210"
masked = mask_pii(text)
# Output: "Call me at +91-XXXX43210"
```

---

## 📄 License

MIT License - See LICENSE file for details

---