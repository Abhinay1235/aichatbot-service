"""SQL service for executing LLM-generated queries safely."""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging
import re

from src.database.models import UberTrip, Base

logger = logging.getLogger(__name__)


class SQLServiceError(Exception):
    """Custom exception for SQL service errors."""
    pass


class SQLService:
    """Service for safely executing LLM-generated SQL queries."""
    
    # Allowed SQL keywords (whitelist approach)
    ALLOWED_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT',
        'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS NULL', 'IS NOT NULL',
        'AS', 'LIMIT', 'OFFSET', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
    }
    
    # Forbidden keywords (blacklist approach)
    FORBIDDEN_KEYWORDS = {
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE',
        'EXEC', 'EXECUTE', 'GRANT', 'REVOKE', 'UNION', '--', ';'
    }
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information for LLM context."""
        try:
            # Get table structure
            table_info = []
            for column in UberTrip.__table__.columns:
                table_info.append({
                    'name': column.name,
                    'type': str(column.type),
                    'nullable': column.nullable
                })
            
            # Get sample data counts
            total_rows = self.db.query(UberTrip).count()
            
            # Get unique values for key columns (for context)
            unique_statuses = [row[0] for row in self.db.query(UberTrip.booking_status).distinct().all()]
            unique_vehicles = [row[0] for row in self.db.query(UberTrip.vehicle_type).distinct().all()]
            unique_payments = [row[0] for row in self.db.query(UberTrip.payment_method).distinct().filter(
                UberTrip.payment_method.isnot(None)
            ).all()]
            
            return {
                'table_name': 'uber_trips',
                'columns': table_info,
                'total_rows': total_rows,
                'sample_values': {
                    'booking_status': unique_statuses,
                    'vehicle_type': unique_vehicles,
                    'payment_method': unique_payments
                },
                'description': 'Uber trip booking and cancellation data'
            }
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            raise SQLServiceError(f"Failed to get schema information: {str(e)}")
    
    def validate_sql(self, sql: str) -> bool:
        """Validate SQL query for safety."""
        sql_upper = sql.upper().strip()
        
        # Check for forbidden keywords
        for forbidden in self.FORBIDDEN_KEYWORDS:
            if forbidden in sql_upper:
                raise SQLServiceError(f"Forbidden SQL keyword detected: {forbidden}")
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            raise SQLServiceError("Only SELECT queries are allowed")
        
        # Check for multiple statements (prevent SQL injection)
        if ';' in sql or sql.count('SELECT') > 1:
            raise SQLServiceError("Multiple statements not allowed")
        
        # Basic syntax check - should contain FROM
        if 'FROM' not in sql_upper:
            raise SQLServiceError("SQL must contain FROM clause")
        
        # Table name should be uber_trips
        if 'UBER_TRIPS' not in sql_upper:
            raise SQLServiceError("Query must reference uber_trips table")
        
        return True
    
    def execute_query(self, sql: str, limit: int = 1000) -> Dict[str, Any]:
        """
        Execute a validated SQL query safely.
        
        Args:
            sql: SQL query string
            limit: Maximum number of rows to return (safety limit)
        
        Returns:
            Dictionary with query results
        """
        try:
            # Validate SQL
            self.validate_sql(sql)
            
            # Add LIMIT if not present (safety measure)
            sql_upper = sql.upper()
            if 'LIMIT' not in sql_upper:
                sql = f"{sql.rstrip(';')} LIMIT {limit}"
            
            # Execute query
            result = self.db.execute(text(sql))
            rows = result.fetchall()
            
            # Get column names
            columns = result.keys()
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                'success': True,
                'data': data,
                'row_count': len(data),
                'columns': list(columns)
            }
            
        except SQLServiceError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"SQL execution error: {e}")
            raise SQLServiceError(f"SQL execution failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise SQLServiceError(f"Unexpected error: {str(e)}")
    
    def format_results_for_llm(self, results: Dict[str, Any]) -> str:
        """Format query results in a way that's easy for LLM to process."""
        if not results['success'] or not results['data']:
            return "No results found."
        
        # Format as a simple text representation
        lines = []
        lines.append(f"Query returned {results['row_count']} rows.")
        lines.append(f"Columns: {', '.join(results['columns'])}")
        lines.append("")
        
        # Show first few rows
        for i, row in enumerate(results['data'][:10], 1):
            lines.append(f"Row {i}:")
            for col, val in row.items():
                lines.append(f"  {col}: {val}")
            lines.append("")
        
        if results['row_count'] > 10:
            lines.append(f"... and {results['row_count'] - 10} more rows")
        
        return "\n".join(lines)

