import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.retriever import initialize_vectorstore
from src.config import settings


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Vector Store Initialization")
    print("=" * 60)
    
    try:
        settings.validate()
        print("✓ Configuration validated")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False
    
    required_files = [
        settings.POLICIES_FILE,
        settings.FAQS_FILE,
        settings.PRODUCTS_FILE,
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    
    if missing_files:
        print("\n✗ Missing required data files:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nPlease ensure all data files are in the data/ directory")
        return False
    
    print("✓ All required data files found")
    
    # Initialize vector store
    print("\nBuilding vector store...")
    success = initialize_vectorstore()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Vector store initialized successfully!")
        print("=" * 60)
        print("\nYou can now run the application:")
        print("  streamlit run app/streamlit_app.py")
        return True
    else:
        print("\n✗ Failed to initialize vector store")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)