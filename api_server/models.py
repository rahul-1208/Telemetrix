from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for natural language query"""
    
    question: str = Field(
        ...,
        description="Natural language question about product usage data",
        example="How many active users did we have last month?",
        min_length=1,
        max_length=1000
    )
    
    tenant_id: str = Field(
        ...,
        description="Tenant identifier for data isolation",
        example="tenant_123"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "question": "How many users signed up in the last 30 days?",
                "tenant_id": "tenant_123"
            }
        }

class SQLResult(BaseModel):
    """Result model for SQL generation"""
    
    sql_query: str = Field(
        ...,
        description="Generated SQL query",
        example="SELECT COUNT(*) FROM users WHERE tenant_id = 'tenant_123' AND signup_date >= CURRENT_DATE - INTERVAL '30 days'"
    )
    
    explanation: Optional[str] = Field(
        None,
        description="Explanation of the generated SQL query",
        example="This query counts all users for the specified tenant who signed up within the last 30 days"
    )

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    
    success: bool = Field(
        ...,
        description="Whether the query was processed successfully"
    )
    
    question: str = Field(
        ...,
        description="Original question that was asked"
    )
    
    sql_query: str = Field(
        ...,
        description="Generated SQL query"
    )
    
    explanation: Optional[str] = Field(
        None,
        description="Explanation of the generated SQL query"
    )
    
    tenant_id: str = Field(
        ...,
        description="Tenant identifier"
    )
    
    # New fields for actual data results
    data: Optional[list] = Field(
        None,
        description="Actual data results from the SQL query"
    )
    
    columns: Optional[list] = Field(
        None,
        description="Column names from the query results"
    )
    
    row_count: Optional[int] = Field(
        None,
        description="Number of rows returned"
    )
    
    error: Optional[str] = Field(
        None,
        description="Error message if query execution failed"
    )
    
    natural_language_response: Optional[str] = Field(
        None,
        description="Human-readable answer generated from the data"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the response was generated"
    )

class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(
        ...,
        description="Health status of the service"
    )
    
    service: str = Field(
        ...,
        description="Name of the service"
    )
    
    version: str = Field(
        ...,
        description="Version of the service"
    )
    
    timestamp: float = Field(
        ...,
        description="Unix timestamp of the health check"
    )

class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(
        ...,
        description="Error type"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Request identifier for tracing"
    ) 