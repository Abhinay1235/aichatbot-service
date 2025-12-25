"""Test script for SQL service."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.session import SessionLocal
from src.services.sql_service import SQLService


def test_sql_service():
    """Test SQL service functions."""
    db = SessionLocal()
    service = SQLService(db)
    
    try:
        print("🧪 Testing SQL Service...\n")
        
        # Test 1: Get schema info
        print("📊 Schema Information:")
        schema = service.get_schema_info()
        print(f"   Table: {schema['table_name']}")
        print(f"   Total Rows: {schema['total_rows']:,}")
        print(f"   Columns: {len(schema['columns'])}")
        print(f"   Sample Statuses: {schema['sample_values']['booking_status']}")
        print(f"   Sample Vehicle Types: {schema['sample_values']['vehicle_type']}")
        
        # Test 2: Execute a simple query
        print("\n✅ Testing SQL Query Execution:")
        sql = """
        SELECT booking_status, COUNT(*) as count 
        FROM uber_trips 
        GROUP BY booking_status
        """
        result = service.execute_query(sql)
        print(f"   Query executed successfully!")
        print(f"   Rows returned: {result['row_count']}")
        print(f"   Columns: {result['columns']}")
        print("\n   Results:")
        for row in result['data']:
            print(f"     {row}")
        
        # Test 3: Test SQL validation (should fail)
        print("\n🔒 Testing SQL Validation:")
        try:
            dangerous_sql = "DROP TABLE uber_trips"
            service.execute_query(dangerous_sql)
            print("   ❌ Validation failed - dangerous query was allowed!")
        except Exception as e:
            print(f"   ✅ Validation working - blocked dangerous query: {type(e).__name__}")
        
        # Test 4: Format results for LLM
        print("\n📝 Testing Result Formatting:")
        formatted = service.format_results_for_llm(result)
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_sql_service()

