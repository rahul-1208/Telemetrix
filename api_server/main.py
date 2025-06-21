from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn
from contextlib import asynccontextmanager
import time
from typing import Dict, Any

from models import QueryRequest, QueryResponse, HealthResponse
from services.nlq_service import NLQService
from config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events"""
    # Startup
    logger.info("Starting SaaS Product Usage Data Assistant API")
    start_time = time.time()
    
    # Initialize services
    try:
        app.state.nlq_service = NLQService()
        logger.info("NLQ Service initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize NLQ Service", error=str(e))
        raise
    
    startup_time = time.time() - start_time
    logger.info("API startup completed", startup_time_ms=startup_time * 1000)
    
    yield
    
    # Shutdown
    logger.info("Shutting down SaaS Product Usage Data Assistant API")

# Create FastAPI app with production settings
app = FastAPI(
    title="SaaS Product Usage Data Assistant",
    description="AI-powered backend service for natural language queries on product usage data",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for production error handling"""
    logger.error("Unhandled exception", 
                error=str(exc), 
                path=request.url.path,
                method=request.method)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Middleware to add request timing and logging"""
    start_time = time.time()
    
    # Add request ID for tracing
    request.state.request_id = f"req_{int(start_time * 1000)}"
    
    logger.info("Incoming request",
                method=request.method,
                path=request.url.path,
                request_id=request.state.request_id)
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info("Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time_ms=process_time * 1000,
                request_id=request.state.request_id)
    
    return response

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        service="SaaS Product Usage Data Assistant",
        version="1.0.0",
        timestamp=time.time()
    )

@app.post("/api/v1/query", response_model=QueryResponse, tags=["Queries"])
async def generate_sql_query(
    request: QueryRequest,
    nlq_service: NLQService = Depends(lambda: app.state.nlq_service)
):
    """
    Generate SQL query from natural language question
    
    This endpoint takes a natural language question about product usage data
    and generates a corresponding SQL query using AI.
    """
    try:
        logger.info("Processing query request",
                   question=request.question,
                   tenant_id=request.tenant_id,
                   request_id=getattr(request, 'request_id', 'unknown'))
        
        # Generate SQL using NLQ service
        sql_result = await nlq_service.generate_sql(
            question=request.question,
            tenant_id=request.tenant_id
        )
        
        logger.info("SQL generation completed",
                   question=request.question,
                   sql_generated=sql_result.sql_query,
                   request_id=getattr(request, 'request_id', 'unknown'))
        
        return QueryResponse(
            success=True,
            question=request.question,
            sql_query=sql_result.sql_query,
            explanation=sql_result.explanation,
            tenant_id=request.tenant_id
        )
        
    except Exception as e:
        logger.error("SQL generation failed",
                    question=request.question,
                    error=str(e),
                    request_id=getattr(request, 'request_id', 'unknown'))
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate SQL query: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 