"""Test script for chat service."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.session import SessionLocal
from src.services.chat_service import ChatService


def test_chat_service():
    """Test chat service with sample questions."""
    db = SessionLocal()
    service = ChatService(db)
    
    try:
        print("🤖 Testing Chat Service...\n")
        
        # Test questions
        test_questions = [
            "How many total trips are there?",
            "What is the average booking value?",
            "How many successful rides were there?",
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"Question {i}: {question}")
            print("-" * 60)
            
            try:
                result = service.process_message(question)
                
                if result['success']:
                    print(f"✅ Response: {result['response']}")
                    print(f"📊 SQL Query: {result.get('sql_query', 'N/A')}")
                    print(f"📈 Results: {result.get('query_results', {})}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    print(f"Response: {result['response']}")
                
            except Exception as e:
                print(f"❌ Exception: {e}")
            
            print("\n" + "=" * 60 + "\n")
        
        print("✅ Chat service test complete!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Check if OpenAI API key is set
    from src.config import settings
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        print("⚠️  Warning: OPENAI_API_KEY not set in .env file")
        print("Please set your OpenAI API key in the .env file before testing.")
        sys.exit(1)
    
    test_chat_service()

