from openai import OpenAI
import structlog
from typing import Optional
from models import SQLResult
from config import settings

logger = structlog.get_logger()

class NLQService:
    """Natural Language Query service for SQL generation"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        
        # Database schema context for your SaaS usage data
        self.database_schema = """
        Database Schema for SaaS Product Usage Analytics:
        
        Table: tenants
        - id (character varying) - Primary key, tenant identifier
        - name (character varying) - Tenant name
        - industry (character varying) - Industry classification
        
        Table: users
        - id (character varying) - Primary key, user identifier
        - tenant_id (character varying) - Foreign key to tenants.id
        - name (character varying) - User's full name
        - email (character varying) - User's email address
        - signup_date (date) - Date when user signed up
        
        Table: features
        - id (character varying) - Primary key, feature identifier
        - name (character varying) - Feature name
        - category (character varying) - Feature category
        
        Table: usage_events
        - id (character varying) - Primary key, event identifier
        - user_id (character varying) - Foreign key to users.id
        - feature_id (character varying) - Foreign key to features.id
        - event_type (character varying) - Type of usage event (e.g., 'login', 'feature_used', 'export')
        - timestamp (timestamp without time zone) - When the event occurred
        
        Relationships:
        - users.tenant_id -> tenants.id (Many-to-One)
        - usage_events.user_id -> users.id (Many-to-One)
        - usage_events.feature_id -> features.id (Many-to-One)
        
        Business Context:
        - This is a multi-tenant SaaS application
        - Each tenant has multiple users
        - Users interact with features, creating usage events
        - All queries must include tenant isolation via tenant_id filter
        """
    
    async def generate_sql(self, question: str, tenant_id: str) -> SQLResult:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question about product usage data
            tenant_id: Tenant identifier for data isolation
            
        Returns:
            SQLResult containing the generated SQL and explanation
        """
        try:
            logger.info("Generating SQL from question", 
                       question=question, 
                       tenant_id=tenant_id)
            
            # Create system message with schema context
            system_message = {
                "role": "system",
                "content": f"""You are a SQL expert specializing in SaaS product usage analytics.
                
                {self.database_schema}
                
                CRITICAL RULES:
                1. ALWAYS include 'tenant_id = '{tenant_id}' in WHERE clause for data isolation
                2. Use only SELECT statements - no INSERT, UPDATE, DELETE, DROP, etc.
                3. Use proper PostgreSQL syntax
                4. Return only the SQL query, no explanations in the query itself
                5. Use appropriate aggregations (COUNT, SUM, AVG, MAX, MIN) when needed
                6. Handle date ranges with PostgreSQL date functions
                7. Join tables appropriately when needed
                8. Use meaningful column aliases for clarity
                
                Common patterns:
                - Active users: users with recent usage_events (last 30 days)
                - Feature adoption: COUNT(DISTINCT user_id) from usage_events
                - User growth: COUNT(*) from users with date filters
                - Usage frequency: COUNT(*) from usage_events with grouping
                """
            }
            
            # Create user message
            user_message = {
                "role": "user",
                "content": question
            }
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[system_message, user_message],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract SQL query
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up any markdown formatting
            sql_query = sql_query.strip("` \n")
            if sql_query.startswith("sql"):
                sql_query = sql_query[3:].strip()
            
            # Generate explanation
            explanation = await self._generate_explanation(question, sql_query)
            
            logger.info("SQL generation successful", 
                       question=question,
                       sql_query=sql_query,
                       tenant_id=tenant_id)
            
            return SQLResult(
                sql_query=sql_query,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error("SQL generation failed", 
                        question=question,
                        error=str(e),
                        tenant_id=tenant_id)
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    async def _generate_explanation(self, question: str, sql_query: str) -> str:
        """
        Generate explanation for the SQL query
        
        Args:
            question: Original user question
            sql_query: Generated SQL query
            
        Returns:
            Explanation of what the SQL query does
        """
        try:
            explanation_prompt = {
                "role": "system",
                "content": """You are a data analyst explaining SQL queries in simple terms.
                
                Provide a brief, business-friendly explanation of what the SQL query does
                and how it answers the user's question. Keep it under 2 sentences."""
            }
            
            user_message = {
                "role": "user",
                "content": f"Question: {question}\n\nSQL Query: {sql_query}\n\nExplain what this query does:"
            }
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[explanation_prompt, user_message],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning("Failed to generate explanation", error=str(e))
            return "Generated SQL query to answer your question about product usage data."
    
    def validate_sql_safety(self, sql_query: str) -> bool:
        """
        Validate that the generated SQL query is safe to execute
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            True if query is safe, False otherwise
        """
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