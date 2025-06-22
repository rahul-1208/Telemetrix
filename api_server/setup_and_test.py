#!/usr/bin/env python3
"""
Setup and test script for the complete integration
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Debug: Print the path to verify
print(f"🔍 Debug: Project root added to path: {project_root}")
print(f"🔍 Debug: Current sys.path: {sys.path[:3]}...")

def setup_database_password():
    """Set up the database password"""
    print("🔧 Database Setup")
    print("=" * 40)
    
    # Check if password is already set in .env
    try:
        from api_server.config import settings
        current_password = settings.DB_PASSWORD
        if current_password:
            print(f"✅ Database password is already set in .env file")
            return True
    except Exception as e:
        print(f"⚠️  Could not check .env file: {e}")
    
    # Get password from user
    print("Please enter your Aiven PostgreSQL password:")
    password = input("Password: ").strip()
    
    if not password:
        print("❌ Password is required!")
        return False
    
    # Note: User should add this to their .env file
    print("✅ Please add the following line to your .env file:")
    print(f"   DB_PASSWORD={password}")
    print("   Then restart this script.")
    return False

def test_database_connection():
    """Test the database connection"""
    print("\n🔍 Testing Database Connection")
    print("=" * 40)
    
    try:
        # Try to import the module
        print("   Trying to import sqlexecutor...")
        from sqlexecutor.db_service import DatabaseService
        print("   ✅ Import successful!")
        
        # Initialize database service
        db_service = DatabaseService()
        
        # Test connection
        if db_service.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"   Current Python path: {sys.path}")
        return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_nlq_service():
    """Test the NLQ service"""
    print("\n🤖 Testing NLQ Service")
    print("=" * 40)
    
    try:
        from api_server.services.nlq_service import NLQService
        
        # Initialize NLQ service
        nlq_service = NLQService()
        
        # Test SQL generation
        import asyncio
        
        async def test_generation():
            result = await nlq_service.generate_sql(
                question="How many users do we have?",
                tenant_id="test_tenant"
            )
            print(f"✅ SQL Generation successful!")
            print(f"   Generated SQL: {result.sql_query}")
            return True
        
        return asyncio.run(test_generation())
        
    except Exception as e:
        print(f"❌ NLQ service error: {e}")
        return False

def test_complete_service():
    """Test the complete service flow"""
    print("\n🔄 Testing Complete Service Flow")
    print("=" * 40)
    
    try:
        from api_server.services.complete_service import CompleteService
        
        # Initialize complete service
        complete_service = CompleteService()
        
        # Test complete flow
        import asyncio
        
        async def test_complete_flow():
            result = await complete_service.process_query(
                question="How many users do we have?",
                tenant_id="test_tenant"
            )
            print(f"✅ Complete flow successful!")
            print(f"   Success: {result.success}")
            print(f"   SQL: {result.sql_query}")
            print(f"   Response: {result.natural_language_response}")
            return result.success
        
        return asyncio.run(test_complete_flow())
        
    except Exception as e:
        print(f"❌ Complete service error: {e}")
        return False

def main():
    print("🚀 SaaS Product Usage Data Assistant - Setup & Test")
    print("=" * 60)
    
    # Step 1: Setup database password
    if not setup_database_password():
        return
    
    # Step 2: Test database connection
    if not test_database_connection():
        print("\n💡 Please check your database credentials and try again.")
        return
    
    # Step 3: Test NLQ service
    if not test_nlq_service():
        print("\n💡 Please check your OpenAI API key and try again.")
        return
    
    # Step 4: Test complete service
    if not test_complete_service():
        print("\n💡 Please check your service configuration and try again.")
        return
    
    print("\n🎉 All tests passed! You can now start the API server:")
    print("   python -m api_server.main")
    
    print("\n📝 To test the complete flow:")
    print("   python api_server/test_complete_flow.py")

if __name__ == "__main__":
    main() 