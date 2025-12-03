# H-002 | Customer Experience Automation MVP

Hyper-Personalized Customer Support Agent using RAG, LangGraph, and Google Gemini.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Google Gemini API key
```

### 3. Generate Dummy Data

```bash
python src/data_loaders/generate_dummy_data.py
```

### 4. Run the MVP

```bash
streamlit run app/streamlit_app.py
```

## 📁 Project Structure

```
customer-experience-agent/
├── data/               # Dummy data (customers, locations, products)
├── src/
│   ├── config/        # Configuration & settings
│   ├── data_loaders/  # Data generation & loading
│   ├── rag/           # Vector store & retrieval
│   ├── agent/         # LangGraph agent logic
│   ├── privacy/       # PII masking utilities
│   └── utils/         # Helper functions
├── app/               # Streamlit UI
└── tests/             # Unit tests
```

## 🎯 Key Features

- ✅ Context-aware conversation (location, history, preferences)
- ✅ RAG pipeline with company policies & FAQs
- ✅ Location-based recommendations
- ✅ PII data masking for privacy
- ✅ Multi-tool agent with LangGraph

## 🛠️ Tech Stack

- **LLM**: Google Gemini 
- **Framework**: LangChain + LangGraph
- **Vector Store**: FAISS
- **UI**: Streamlit
- **Privacy**: Presidio

## 📝 Demo Scenarios

1. **"I'm cold"** → AI suggests nearby warm beverage with coupon
2. **"Where's my order?"** → Retrieves order status from customer history
3. **"I need a refund"** → Pulls policy docs and guides user
4. **"What's near me?"** → Shows nearby stores and offers

## 🔒 Privacy & Security

- PII (phone numbers, emails) masked before LLM calls
- Customer data stored locally (dummy data for demo)
- No real customer information used