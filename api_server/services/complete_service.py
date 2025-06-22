"""
Complete service that handles the full NLQ to natural language response flow
"""

import structlog
from typing import Optional, List, Dict, Any
import asyncio

from api_server.models import SQLResult, QueryResponse
from api_server.services.nlq_service import NLQService
from sqlexecutor.db_service import DatabaseService

logger = structlog.get_logger()

class CompleteService:
    """Service that handles the complete NLQ to natural language response flow"""
    
    def __init__(self):
        self.nlq_service = NLQService()
        self.db_service = DatabaseService()
    
    async def process_query(self, question: str, tenant_id: str) -> QueryResponse:
        """
        Process a natural language query and return a complete response
        
        This method:
        1. Generates SQL from the natural language question
        2. Executes the SQL query
        3. Converts the results to natural language
        4. Returns the complete response
        """
        try:
            logger.info("Starting complete query processing", 
                       question=question, tenant_id=tenant_id)
            
            # Step 1: Generate SQL from natural language
            sql_result = await self.nlq_service.generate_sql(
                question=question,
                tenant_id=tenant_id
            )
            
            logger.info("SQL generated successfully", 
                       sql_query=sql_result.sql_query)
            
            # Step 2: Execute the SQL query
            db_result = await self._execute_sql(sql_result.sql_query, tenant_id)
            
            # Step 3: Generate natural language response
            natural_response = await self._generate_natural_response(
                question=question,
                sql_query=sql_result.sql_query,
                data=db_result.get('data', []),
                columns=db_result.get('columns', []),
                row_count=db_result.get('row_count', 0)
            )
            
            # Step 4: Build complete response
            response = QueryResponse(
                success=True,
                question=question,
                sql_query=sql_result.sql_query,
                explanation=sql_result.explanation,
                tenant_id=tenant_id,
                data=db_result.get('data'),
                columns=db_result.get('columns'),
                row_count=db_result.get('row_count'),
                natural_language_response=natural_response
            )
            
            logger.info("Complete query processing successful",
                       question=question, row_count=db_result.get('row_count'))
            
            return response
            
        except Exception as e:
            logger.error("Complete query processing failed",
                        question=question, error=str(e))
            
            # Return error response
            return QueryResponse(
                success=False,
                question=question,
                sql_query="",
                explanation="",
                tenant_id=tenant_id,
                error=str(e),
                natural_language_response=f"Sorry, I couldn't process your question: {str(e)}"
            )
    
    async def _execute_sql(self, sql_query: str, tenant_id: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        try:
            # For now, we'll return mock data since we haven't fully integrated the database
            # In the real implementation, this would call self.db_service.execute_query()
            
            logger.info("Executing SQL query", sql_query=sql_query)
            
            # Mock data based on the type of query
            if "COUNT" in sql_query.upper():
                return {
                    'data': [{'total_users': 1250}],
                    'columns': ['total_users'],
                    'row_count': 1
                }
            elif "POPULAR" in sql_query.upper() or "FEATURES" in sql_query.upper():
                return {
                    'data': [
                        {'feature_name': 'Dashboard Analytics', 'total_events': 15420},
                        {'feature_name': 'User Management', 'total_events': 12340},
                        {'feature_name': 'Reporting', 'total_events': 9870}
                    ],
                    'columns': ['feature_name', 'total_events'],
                    'row_count': 3
                }
            elif "ACTIVITY" in sql_query.upper() or "LAST" in sql_query.upper():
                return {
                    'data': [
                        {'user_name': 'John Doe', 'user_email': 'john@example.com', 'event_type': 'login', 'timestamp': '2024-01-15'},
                        {'user_name': 'Jane Smith', 'user_email': 'jane@example.com', 'event_type': 'feature_used', 'timestamp': '2024-01-14'}
                    ],
                    'columns': ['user_name', 'user_email', 'event_type', 'timestamp'],
                    'row_count': 2
                }
            else:
                return {
                    'data': [{'result': 'Data retrieved successfully'}],
                    'columns': ['result'],
                    'row_count': 1
                }
                
        except Exception as e:
            logger.error("SQL execution failed", sql_query=sql_query, error=str(e))
            raise
    
    async def _generate_natural_response(
        self, 
        question: str, 
        sql_query: str, 
        data: List[Dict], 
        columns: List[str], 
        row_count: int
    ) -> str:
        """Generate natural language response from query results"""
        try:
            logger.info("Generating natural language response",
                       question=question, row_count=row_count)
            
            # For now, we'll create a simple natural language response
            # In the real implementation, this would call OpenAI to generate a response
            
            if row_count == 0:
                return f"Based on your question '{question}', I found no data matching your criteria."
            
            if "COUNT" in sql_query.upper():
                count_value = data[0].get('total_users', data[0].get(list(data[0].keys())[0]))
                return f"You have {count_value} users in your system."
            
            elif "POPULAR" in question.upper() or "FEATURES" in question.upper():
                if row_count == 1:
                    feature = data[0]['feature_name']
                    events = data[0]['total_events']
                    return f"The most popular feature is {feature} with {events} usage events."
                else:
                    top_feature = data[0]['feature_name']
                    top_events = data[0]['total_events']
                    return f"The most popular feature is {top_feature} with {top_events} usage events. I found {row_count} features in total."
            
            elif "ACTIVITY" in question.upper() or "LAST" in question.upper():
                return f"I found {row_count} user activities in the specified time period. The most recent activity was by {data[0]['user_name']} ({data[0]['event_type']})."
            
            else:
                return f"I found {row_count} results for your question '{question}'. The data shows various insights based on your query."
                
        except Exception as e:
            logger.error("Natural language response generation failed",
                        question=question, error=str(e))
            return f"I processed your question '{question}' and found {row_count} results, but I couldn't generate a natural language summary due to an error." 