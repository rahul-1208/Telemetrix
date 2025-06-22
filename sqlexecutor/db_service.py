import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional
import logging
from .db_config import db_config

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for executing SQL queries against Aiven PostgreSQL"""
    
    def __init__(self):
        self.config = db_config
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with psycopg2.connect(**self.config.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    self.logger.info("Database connection successful")
                    return result[0] == 1
        except Exception as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            return False
    
    def execute_query(self, sql_query: str, tenant_id: str) -> Dict[str, Any]:
        """
        Execute SQL query with tenant isolation
        
        Args:
            sql_query: SQL query to execute
            tenant_id: Tenant identifier for isolation
            
        Returns:
            Dictionary containing query results and metadata
        """
        try:
            # Validate query safety
            if not self._is_query_safe(sql_query):
                raise ValueError("Query contains unsafe operations")
            
            # Ensure tenant isolation
            if not self._has_tenant_isolation(sql_query, tenant_id):
                raise ValueError("Query must include tenant isolation")
            
            # Execute query
            with psycopg2.connect(**self.config.connection_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(sql_query)
                    
                    # Fetch results
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        results = [dict(row) for row in rows]
                    else:
                        columns = []
                        results = []
                    
                    return {
                        "success": True,
                        "data": results,
                        "columns": columns,
                        "row_count": len(results),
                        "sql_query": sql_query,
                        "tenant_id": tenant_id
                    }
                    
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sql_query": sql_query,
                "tenant_id": tenant_id
            }
    
    def _is_query_safe(self, sql_query: str) -> bool:
        """Check if SQL query is safe to execute"""
        query_upper = sql_query.upper().strip()
        
        # Must start with SELECT
        if not query_upper.startswith('SELECT'):
            return False
        
        # Check for dangerous keywords
        dangerous_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER',
            'CREATE', 'GRANT', 'REVOKE', 'EXECUTE', 'EXEC', 'UNION'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        return True
    
    def _has_tenant_isolation(self, sql_query: str, tenant_id: str) -> bool:
        """Verify that query includes tenant isolation"""
        query_lower = sql_query.lower()
        tenant_condition = f"tenant_id = '{tenant_id}'"
        
        return tenant_condition in query_lower
    
    def get_schema_info(self) -> str:
        """Get database schema information"""
        try:
            with psycopg2.connect(**self.config.connection_params) as conn:
                with conn.cursor() as cursor:
                    # Query to get table information
                    schema_query = """
                    SELECT 
                        table_name,
                        column_name,
                        data_type,
                        is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    AND table_name IN (
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    )
                    ORDER BY table_name, ordinal_position;
                    """
                    
                    cursor.execute(schema_query)
                    schema_data = cursor.fetchall()
                    
                    # Format schema information
                    schema_info = "Database Schema:\n"
                    current_table = None
                    
                    for row in schema_data:
                        table_name, column_name, data_type, is_nullable = row
                        
                        if table_name != current_table:
                            schema_info += f"\nTable: {table_name}\n"
                            current_table = table_name
                        
                        nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                        schema_info += f"- {column_name} ({data_type}) {nullable}\n"
                    
                    return schema_info
                    
        except Exception as e:
            self.logger.error(f"Failed to get schema: {str(e)}")
            return "Error retrieving schema information" 