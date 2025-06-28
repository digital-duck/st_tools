# File: example_files.py
"""
Example Code Files
Contains templates for Flask, FastAPI, and migration example files
"""


def get_flask_example() -> str:
    """Generate Flask example file"""
    return '''"""
Basic Flask Application Example
Chapter 1-3: Demonstrates traditional Flask patterns before migration

This example shows a typical Flask application with:
- Synchronous request handling
- SQLAlchemy ORM (sync)
- Traditional route definitions
- Manual validation and serialization

Usage:
    python src/flask_examples/basic_app.py
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    """User model for demonstration"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Routes
@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Flask Application", 
        "version": "1.0",
        "framework": "Flask (Synchronous)"
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "database": "connected"
    })


@app.route('/users', methods=['GET'])
def get_users():
    """Get all users - synchronous operation"""
    start_time = time.time()
    
    # Simulate database query delay
    time.sleep(0.1)
    
    users = User.query.all()
    result = [user.to_dict() for user in users]
    
    processing_time = time.time() - start_time
    
    logger.info(f"Retrieved {len(result)} users in {processing_time:.3f}s")
    
    return jsonify({
        "users": result,
        "count": len(result),
        "processing_time": processing_time,
        "note": "This is a synchronous operation - blocks other requests"
    })


@app.route('/users', methods=['POST'])
def create_user():
    """Create new user - synchronous operation"""
    data = request.get_json()
    
    # Manual validation
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email required"}), 400
    
    if '@' not in data['email']:
        return jsonify({"error": "Invalid email format"}), 400
    
    # Check if user exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 409
    
    # Simulate validation delay
    time.sleep(0.05)
    
    try:
        user = User(name=data['name'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Created user: {user.email}")
        return jsonify(user.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user: {e}")
        return jsonify({"error": "Failed to create user"}), 500


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user - synchronous operation"""
    # Simulate database lookup delay
    time.sleep(0.05)
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict())


@app.route('/slow-operation', methods=['GET'])
def slow_operation():
    """Simulate slow operation that blocks other requests"""
    logger.info("Starting slow operation...")
    
    # This blocks the entire thread - other requests must wait
    time.sleep(2)
    
    logger.info("Slow operation completed")
    return jsonify({
        "message": "Slow operation completed",
        "note": "This blocked all other requests for 2 seconds"
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    print("\\n" + "="*50)
    print("Starting Flask Application")
    print("="*50)
    print("📍 URL: http://localhost:5000")
    print("📖 Endpoints:")
    print("   GET  /              - Home")
    print("   GET  /health        - Health check")
    print("   GET  /users         - List users")
    print("   POST /users         - Create user")
    print("   GET  /users/<id>    - Get user by ID")
    print("   GET  /slow-operation - Slow blocking operation")
    print("\\n⚠️  Note: This is a synchronous application")
    print("   - Requests are processed sequentially")
    print("   - Slow operations block other requests")
    print("   - No async/await patterns")
    print("="*50)
    
    app.run(debug=True, port=5000, threaded=True)
'''


def get_fastapi_example() -> str:
    """Generate FastAPI example file"""
    return '''"""
Basic FastAPI Application Example
Chapter 4-6: Demonstrates async FastAPI patterns after migration

This example shows the FastAPI equivalent with:
- Asynchronous request handling
- Pydantic models for validation
- Modern route definitions with type hints
- Automatic documentation generation

Usage:
    python src/fastapi_examples/basic_app.py
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app with metadata
app = FastAPI(
    title="FastAPI Async Example",
    description="Demonstrates async patterns for Flask migration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# In-memory storage for demo (in real app, use async database)
users_db: List[dict] = []
user_counter = 0


# Pydantic models for automatic validation
class UserCreate(BaseModel):
    """User creation model with validation"""
    name: str = Field(..., min_length=1, max_length=80, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }
    }


class UserResponse(BaseModel):
    """User response model"""
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: float
    database: str
    uptime: float


class UsersListResponse(BaseModel):
    """Users list response model"""
    users: List[UserResponse]
    count: int
    processing_time: float
    note: str


# Dependency for simulating database session
async def get_db_session():
    """Simulate async database session"""
    # In real app, this would return async database session
    await asyncio.sleep(0.001)  # Simulate connection time
    return "async_db_session"


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("FastAPI application starting up...")
    logger.info("Async database connections initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("FastAPI application shutting down...")


# Routes
@app.get("/", response_model=dict)
async def home():
    """Home endpoint with async processing"""
    # Simulate some async work
    await asyncio.sleep(0.01)
    
    return {
        "message": "FastAPI Application", 
        "version": "1.0.0",
        "framework": "FastAPI (Asynchronous)",
        "features": ["async/await", "type hints", "automatic validation", "OpenAPI docs"]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Async health check endpoint"""
    # Simulate async health checks
    await asyncio.sleep(0.01)
    
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        database="connected",
        uptime=time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    )


@app.get("/users", response_model=UsersListResponse)
async def get_users(db_session=Depends(get_db_session)):
    """Get all users - asynchronous operation"""
    start_time = time.time()
    
    # Simulate async database query delay (non-blocking)
    await asyncio.sleep(0.1)
    
    processing_time = time.time() - start_time
    
    logger.info(f"Retrieved {len(users_db)} users in {processing_time:.3f}s (async)")
    
    return UsersListResponse(
        users=[UserResponse(**user) for user in users_db],
        count=len(users_db),
        processing_time=processing_time,
        note="This is an async operation - doesn't block other requests"
    )


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db_session=Depends(get_db_session)):
    """Create new user - asynchronous operation with automatic validation"""
    global user_counter
    
    # Check if user exists (async)
    await asyncio.sleep(0.02)  # Simulate async database check
    
    existing_user = next((u for u in users_db if u['email'] == user_data.email), None)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Simulate async validation delay (non-blocking)
    await asyncio.sleep(0.05)
    
    user_counter += 1
    new_user = {
        "id": user_counter,
        "name": user_data.name,
        "email": user_data.email,
        "created_at": datetime.now()
    }
    
    users_db.append(new_user)
    
    logger.info(f"Created user: {new_user['email']} (async)")
    return UserResponse(**new_user)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db_session=Depends(get_db_session)):
    """Get single user - asynchronous operation"""
    # Simulate async database lookup delay (non-blocking)
    await asyncio.sleep(0.05)
    
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse(**user)


@app.get("/slow-operation")
async def slow_operation():
    """Simulate slow operation that doesn't block other requests"""
    logger.info("Starting slow async operation...")
    
    # This doesn't block other requests - they can run concurrently
    await asyncio.sleep(2)
    
    logger.info("Slow async operation completed")
    return {
        "message": "Slow operation completed (async)",
        "note": "This didn't block other requests - they could run concurrently"
    }


@app.get("/concurrent-demo")
async def concurrent_demo():
    """Demonstrate concurrent operations"""
    async def fetch_data(delay: float, data_id: int):
        """Simulate async data fetching"""
        await asyncio.sleep(delay)
        return f"Data {data_id} fetched after {delay}s"
    
    start_time = time.time()
    
    # These operations run concurrently
    tasks = [
        fetch_data(0.5, 1),
        fetch_data(0.3, 2), 
        fetch_data(0.7, 3)
    ]
    
    results = await asyncio.gather(*tasks)
    processing_time = time.time() - start_time
    
    return {
        "results": results,
        "processing_time": processing_time,
        "note": "All operations ran concurrently - total time ≈ max(individual times)",
        "sequential_time_would_be": 0.5 + 0.3 + 0.7,
        "actual_concurrent_time": processing_time
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": str(exc)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    # Store startup time
    app.state.start_time = time.time()
    
    print("\\n" + "="*60)
    print("Starting FastAPI Application")
    print("="*60)
    print("📍 URL: http://localhost:8000")
    print("📖 Interactive Docs: http://localhost:8000/docs")
    print("📋 ReDoc: http://localhost:8000/redoc")
    print("\\n🚀 Endpoints:")
    print("   GET  /                 - Home")
    print("   GET  /health           - Health check")
    print("   GET  /users            - List users")
    print("   POST /users            - Create user (with validation)")
    print("   GET  /users/{id}       - Get user by ID")
    print("   GET  /slow-operation   - Slow non-blocking operation")
    print("   GET  /concurrent-demo  - Concurrent operations demo")
    print("\\n✨ Features:")
    print("   - Asynchronous request handling")
    print("   - Automatic request/response validation")
    print("   - Interactive API documentation")
    print("   - Type hints and modern Python patterns")
    print("   - Concurrent request processing")
    print("="*60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
'''


def get_async_patterns_example() -> str:
    """Generate async patterns example file"""
    return '''"""
Async Programming Patterns Example
Chapter 2-3: Demonstrates fundamental async concepts for Flask to FastAPI migration

This comprehensive example covers:
- Basic async/await patterns
- Concurrent vs sequential execution
- Async context managers
- Error handling in async code
- Real-world async patterns

Usage:
    python src/async_patterns/async_basics.py
"""

import asyncio
import aiohttp
import time
import random
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 1. Basic Async Patterns
async def basic_async_example():
    """Demonstrate basic async/await patterns"""
    print("\\n" + "="*50)
    print("1. BASIC ASYNC PATTERNS")
    print("="*50)
    
    async def async_operation(name: str, delay: float) -> str:
        """Simulate an async operation"""
        print(f"  🚀 Starting {name}...")
        await asyncio.sleep(delay)
        print(f"  ✅ Completed {name}")
        return f"Result from {name}"
    
    # Sequential execution (like synchronous code)
    print("\\n📊 Sequential execution:")
    start_time = time.time()
    result1 = await async_operation("Operation 1", 1.0)
    result2 = await async_operation("Operation 2", 0.5)
    sequential_time = time.time() - start_time
    print(f"  ⏱️  Sequential took: {sequential_time:.2f}s")
    
    # Concurrent execution (async advantage)
    print("\\n🚀 Concurrent execution:")
    start_time = time.time()
    result1, result2 = await asyncio.gather(
        async_operation("Operation A", 1.0),
        async_operation("Operation B", 0.5)
    )
    concurrent_time = time.time() - start_time
    print(f"  ⏱️  Concurrent took: {concurrent_time:.2f}s")
    print(f"  📈 Speedup: {sequential_time/concurrent_time:.2f}x")


# 2. HTTP Requests Pattern
async def async_http_requests():
    """Demonstrate async HTTP requests vs sync approach"""
    print("\\n" + "="*50)
    print("2. ASYNC HTTP REQUESTS")
    print("="*50)
    
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1", 
        "https://httpbin.org/delay/1"
    ]
    
    async def fetch_url(session: aiohttp.ClientSession, url: str, request_id: int) -> Dict[str, Any]:
        """Fetch single URL asynchronously"""
        try:
            print(f"  🌐 Starting request {request_id}")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                data = await response.json()
                print(f"  ✅ Completed request {request_id}")
                return {
                    "request_id": request_id,
                    "url": url, 
                    "status": response.status, 
                    "data": data
                }
        except Exception as e:
            print(f"  ❌ Failed request {request_id}: {e}")
            return {"request_id": request_id, "url": url, "error": str(e)}
    
    # Simulate synchronous approach timing
    sync_time = len(urls) * 1  # Each request takes ~1 second
    print(f"📊 Synchronous approach would take: ~{sync_time}s")
    
    # Async approach
    print("\\n🚀 Making concurrent async requests...")
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url, i+1) for i, url in enumerate(urls)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        async_time = time.time() - start_time
        print(f"  ⏱️  Async total: {async_time:.2f}s")
        print(f"  📈 Speedup: {sync_time/async_time:.2f}x")
        
    except Exception as e:
        print(f"  ❌ HTTP requests failed: {e}")
        print("  💡 This might be due to network connectivity")


# 3. Database Simulation Pattern
async def async_database_pattern():
    """Simulate async database operations"""
    print("\\n" + "="*50)
    print("3. ASYNC DATABASE PATTERNS")
    print("="*50)
    
    async def simulate_db_query(query: str, delay: float) -> Dict[str, Any]:
        """Simulate async database query"""
        print(f"  🗄️  Executing: {query}")
        await asyncio.sleep(delay)  # Simulate I/O wait
        return {
            "query": query,
            "results": f"Mock results for {query}",
            "execution_time": delay,
            "rows_affected": random.randint(1, 100)
        }
    
    # Simulate multiple database operations
    queries = [
        ("SELECT * FROM users WHERE active = true", 0.3),
        ("SELECT * FROM orders WHERE date > '2024-01-01'", 0.5),
        ("SELECT * FROM products WHERE category = 'electronics'", 0.2),
    ]
    
    print("📊 Sequential database queries:")
    start_time = time.time()
    for query, delay in queries:
        result = await simulate_db_query(query, delay)
        print(f"    ✅ {result['rows_affected']} rows")
    sequential_db_time = time.time() - start_time
    
    print("\\n🚀 Concurrent database queries:")
    start_time = time.time()
    
    # Execute all queries concurrently
    tasks = [simulate_db_query(query, delay) for query, delay in queries]
    results = await asyncio.gather(*tasks)
    
    concurrent_db_time = time.time() - start_time
    theoretical_sync_time = sum(delay for _, delay in queries)
    
    total_rows = sum(r['rows_affected'] for r in results)
    print(f"    ✅ Total rows processed: {total_rows}")
    print(f"  ⏱️  Concurrent execution: {concurrent_db_time:.2f}s")
    print(f"  📊 Sequential would take: {theoretical_sync_time:.2f}s")
    print(f"  📈 Efficiency gain: {theoretical_sync_time/concurrent_db_time:.2f}x")


# 4. Async Context Managers
async def async_context_manager_example():
    """Demonstrate async context managers"""
    print("\\n" + "="*50)
    print("4. ASYNC CONTEXT MANAGERS")
    print("="*50)
    
    class AsyncDatabaseConnection:
        """Example async context manager for database connections"""
        
        def __init__(self, connection_string: str):
            self.connection_string = connection_string
            self.connected = False
            self.connection_id = random.randint(1000, 9999)
        
        async def __aenter__(self):
            print(f"  🔌 Opening connection {self.connection_id}...")
            await asyncio.sleep(0.1)  # Simulate connection time
            self.connected = True
            print(f"  ✅ Connection {self.connection_id} established")
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print(f"  🔒 Closing connection {self.connection_id}...")
            await asyncio.sleep(0.05)  # Simulate cleanup time
            self.connected = False
            print(f"  ✅ Connection {self.connection_id} closed")
            
            if exc_type:
                print(f"  ⚠️  Exception occurred: {exc_type.__name__}")
        
        async def execute(self, query: str):
            """Execute a query"""
            if not self.connected:
                raise RuntimeError("Database not connected")
            print(f"    📝 Executing: {query}")
            await asyncio.sleep(0.1)
            return f"Query result: {query} completed"
    
    # Use async context manager
    print("🗄️  Using async context manager for database operations:")
    
    try:
        async with AsyncDatabaseConnection("postgresql://localhost/mydb") as db:
            result1 = await db.execute("INSERT INTO users (name) VALUES ('Alice')")
            result2 = await db.execute("SELECT * FROM users WHERE id = 1")
            print(f"    📊 {result1}")
            print(f"    📊 {result2}")
    except Exception as e:
        print(f"    ❌ Database operation failed: {e}")
    
    print("  💡 Context manager automatically handled connection lifecycle")


# 5. Error Handling Patterns
async def async_error_handling():
    """Demonstrate async error handling patterns"""
    print("\\n" + "="*50)
    print("5. ASYNC ERROR HANDLING")
    print("="*50)
    
    async def unreliable_operation(name: str, should_fail: bool = False, delay: float = 0.1):
        """Operation that might fail"""
        await asyncio.sleep(delay)
        if should_fail:
            raise ValueError(f"Operation {name} failed as expected")
        return f"Success: {name}"
    
    operations = [
        ("Operation 1", False, 0.1),
        ("Operation 2", True, 0.2),   # This will fail
        ("Operation 3", False, 0.15),
        ("Operation 4", True, 0.05),  # This will also fail
    ]
    
    # Handle errors gracefully with asyncio.gather
    print("🛡️  Graceful error handling with return_exceptions=True:")
    
    tasks = [unreliable_operation(name, should_fail, delay) 
             for name, should_fail, delay in operations]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        name = operations[i][0]
        if isinstance(result, Exception):
            print(f"  ❌ {name}: {result}")
        else:
            print(f"  ✅ {name}: {result}")
    
    # Alternative: Individual try-catch for each operation
    print("\\n🔄 Individual error handling:")
    
    async def safe_operation(name: str, should_fail: bool, delay: float):
        try:
            result = await unreliable_operation(name, should_fail, delay)
            return {"name": name, "status": "success", "result": result}
        except Exception as e:
            return {"name": name, "status": "error", "error": str(e)}
    
    safe_tasks = [safe_operation(name, should_fail, delay) 
                  for name, should_fail, delay in operations]
    safe_results = await asyncio.gather(*safe_tasks)
    
    for result in safe_results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        content = result.get("result", result.get("error"))
        print(f"  {status_icon} {result['name']}: {content}")


# 6. Producer-Consumer Pattern
async def producer_consumer_pattern():
    """Demonstrate producer-consumer pattern with async queues"""
    print("\\n" + "="*50)
    print("6. PRODUCER-CONSUMER PATTERN")
    print("="*50)
    
    async def producer(queue: asyncio.Queue, producer_id: int, item_count: int):
        """Produce items and put them in queue"""
        print(f"  🏭 Producer {producer_id} starting...")
        
        for i in range(item_count):
            item = f"Item-{producer_id}-{i+1}"
            await queue.put(item)
            print(f"    📦 Producer {producer_id} created: {item}")
            await asyncio.sleep(0.1)  # Simulate production time
        
        print(f"  🏁 Producer {producer_id} finished")
    
    async def consumer(queue: asyncio.Queue, consumer_id: int):
        """Consume items from queue"""
        print(f"  🤖 Consumer {consumer_id} starting...")
        processed_count = 0
        
        while True:
            try:
                # Wait for item with timeout
                item = await asyncio.wait_for(queue.get(), timeout=1.0)
                print(f"    ⚙️  Consumer {consumer_id} processing: {item}")
                await asyncio.sleep(0.2)  # Simulate processing time
                queue.task_done()
                processed_count += 1
                
            except asyncio.TimeoutError:
                print(f"  🏁 Consumer {consumer_id} finished (timeout), processed {processed_count} items")
                break
    
    # Create queue and start producers/consumers
    queue = asyncio.Queue(maxsize=5)
    
    print("🚀 Starting producer-consumer simulation...")
    
    # Start producers and consumers concurrently
    await asyncio.gather(
        producer(queue, 1, 3),
        producer(queue, 2, 2),
        consumer(queue, 1),
        consumer(queue, 2)
    )
    
    print("  ✅ Producer-consumer pattern completed")


# 7. Real-World Migration Example
async def migration_example():
    """Demonstrate a realistic Flask-to-FastAPI migration scenario"""
    print("\\n" + "="*50)
    print("7. REAL-WORLD MIGRATION EXAMPLE")
    print("="*50)
    
    # Simulate Flask-style synchronous user service
    class FlaskUserService:
        """Traditional Flask-style service (synchronous)"""
        
        def get_user_profile(self, user_id: int) -> Dict[str, Any]:
            """Get user profile (blocks thread)"""
            time.sleep(0.2)  # Simulate database query
            return {"id": user_id, "name": f"User {user_id}", "profile": "basic"}
        
        def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
            """Get user orders (blocks thread)"""
            time.sleep(0.3)  # Simulate database query
            return [{"id": i, "user_id": user_id, "amount": 100 * i} for i in range(1, 4)]
        
        def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
            """Get user preferences (blocks thread)"""
            time.sleep(0.1)  # Simulate database query
            return {"theme": "dark", "notifications": True}
    
    # FastAPI-style asynchronous user service
    class FastAPIUserService:
        """Modern FastAPI-style service (asynchronous)"""
        
        async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
            """Get user profile (non-blocking)"""
            await asyncio.sleep(0.2)  # Simulate async database query
            return {"id": user_id, "name": f"User {user_id}", "profile": "premium"}
        
        async def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
            """Get user orders (non-blocking)"""
            await asyncio.sleep(0.3)  # Simulate async database query
            return [{"id": i, "user_id": user_id, "amount": 150 * i} for i in range(1, 4)]
        
        async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
            """Get user preferences (non-blocking)"""
            await asyncio.sleep(0.1)  # Simulate async database query
            return {"theme": "light", "notifications": True, "language": "en"}
    
    # Demonstrate the difference
    user_id = 123
    
    print("📊 Flask-style sequential processing:")
    flask_service = FlaskUserService()
    start_time = time.time()
    
    profile = flask_service.get_user_profile(user_id)
    orders = flask_service.get_user_orders(user_id)
    preferences = flask_service.get_user_preferences(user_id)
    
    flask_time = time.time() - start_time
    print(f"  ⏱️  Flask approach took: {flask_time:.2f}s")
    print(f"  📊 Profile: {profile['name']}")
    print(f"  📊 Orders count: {len(orders)}")
    print(f"  📊 Theme: {preferences['theme']}")
    
    print("\\n🚀 FastAPI-style concurrent processing:")
    fastapi_service = FastAPIUserService()
    start_time = time.time()
    
    # All operations run concurrently
    profile, orders, preferences = await asyncio.gather(
        fastapi_service.get_user_profile(user_id),
        fastapi_service.get_user_orders(user_id),
        fastapi_service.get_user_preferences(user_id)
    )
    
    fastapi_time = time.time() - start_time
    print(f"  ⏱️  FastAPI approach took: {fastapi_time:.2f}s")
    print(f"  📊 Profile: {profile['name']}")
    print(f"  📊 Orders count: {len(orders)}")
    print(f"  📊 Theme: {preferences['theme']}")
    print(f"  📈 Speedup: {flask_time/fastapi_time:.2f}x")
    
    print("\\n💡 Key migration benefits:")
    print("  • Non-blocking I/O operations")
    print("  • Concurrent request processing")
    print("  • Better resource utilization")
    print("  • Improved application responsiveness")


# Main execution function
async def main():
    """Run all async pattern examples"""
    print("🚀 ASYNC PROGRAMMING PATTERNS")
    print("From Flask to FastAPI Migration Guide")
    print("=" * 60)
    
    examples = [
        ("Basic Async Patterns", basic_async_example),
        ("HTTP Requests", async_http_requests),
        ("Database Patterns", async_database_pattern),
        ("Context Managers", async_context_manager_example),
        ("Error Handling", async_error_handling),
        ("Producer-Consumer", producer_consumer_pattern),
        ("Migration Example", migration_example)
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
            await asyncio.sleep(0.5)  # Brief pause between examples
        except Exception as e:
            print(f"\\n❌ Error in {name}: {e}")
            logger.exception(f"Exception in {name}")
    
    print("\\n" + "="*60)
    print("✅ ALL ASYNC EXAMPLES COMPLETED")
    print("="*60)
    print("\\n📚 Key Takeaways:")
    print("  1. async/await enables concurrent execution")
    print("  2. I/O-bound operations benefit most from async")
    print("  3. Proper error handling is crucial in async code")
    print("  4. Context managers help manage resources")
    print("  5. Producer-consumer patterns handle data flows")
    print("  6. Migration from Flask to FastAPI unlocks concurrency")
    print("\\n🎯 Next Steps:")
    print("  • Study the FastAPI example application")
    print("  • Practice converting Flask routes to FastAPI")
    print("  • Implement async database operations")
    print("  • Add proper error handling and logging")


if __name__ == "__main__":
    # Configure event loop for Windows compatibility
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the async main function
    asyncio.run(main())
'''


def get_migration_example() -> str:
    """Generate migration helper example"""
    return '''"""
Migration Helper Tools
Chapter 4-5: Utilities for converting Flask code to FastAPI

This module provides helper functions and classes to assist in migrating
Flask applications to FastAPI, including route conversion, model migration,
and pattern transformation utilities.

Usage:
    from migration_tools.migration_helper import FlaskToFastAPIConverter
    
    converter = FlaskToFastAPIConverter()
    fastapi_route = converter.convert_flask_route(flask_route_function)
"""

import re
import ast
import inspect
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum


class RouteMethod(Enum):
    """HTTP methods supported in route conversion"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class FlaskRoute:
    """Represents a Flask route for conversion"""
    path: str
    methods: List[str]
    function_name: str
    function_code: str
    parameters: List[str]
    return_type: Optional[str] = None


@dataclass
class FastAPIRoute:
    """Represents the converted FastAPI route"""
    path: str
    method: str
    function_name: str
    function_code: str
    pydantic_models: List[str]
    dependencies: List[str]


class FlaskToFastAPIConverter:
    """Main converter class for Flask to FastAPI migration"""
    
    def __init__(self):
        self.pydantic_models: Dict[str, str] = {}
        self.dependencies: List[str] = []
    
    def convert_flask_route(self, flask_function: Callable) -> FastAPIRoute:
        """Convert a Flask route function to FastAPI equivalent"""
        
        # Extract Flask route information
        flask_route = self._extract_flask_route_info(flask_function)
        
        # Convert to FastAPI
        fastapi_route = self._convert_to_fastapi(flask_route)
        
        return fastapi_route
    
    def _extract_flask_route_info(self, func: Callable) -> FlaskRoute:
        """Extract route information from Flask function"""
        
        # Get function source code
        source = inspect.getsource(func)
        
        # Parse route decorator
        route_pattern = r'@app\.route\([\'"]([^\'"]*)[\'"](?:.*methods=\[([^\]]*)\])?.*\)'
        route_match = re.search(route_pattern, source)
        
        if not route_match:
            raise ValueError("No Flask route decorator found")
        
        path = route_match.group(1)
        methods_str = route_match.group(2) or "'GET'"
        methods = [m.strip('\'"') for m in methods_str.split(',')]
        
        # Extract function parameters
        sig = inspect.signature(func)
        parameters = list(sig.parameters.keys())
        
        return FlaskRoute(
            path=path,
            methods=methods,
            function_name=func.__name__,
            function_code=source,
            parameters=parameters,
            return_type=str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else None
        )
    
    def _convert_to_fastapi(self, flask_route: FlaskRoute) -> FastAPIRoute:
        """Convert Flask route to FastAPI equivalent"""
        
        # Convert path parameters
        fastapi_path = self._convert_path_parameters(flask_route.path)
        
        # Convert function to async
        fastapi_code = self._convert_function_to_async(flask_route)
        
        # Generate Pydantic models if needed
        models = self._generate_pydantic_models(flask_route)
        
        # Determine primary HTTP method
        primary_method = flask_route.methods[0] if flask_route.methods else "GET"
        
        return FastAPIRoute(
            path=fastapi_path,
            method=primary_method,
            function_name=flask_route.function_name,
            function_code=fastapi_code,
            pydantic_models=models,
            dependencies=self.dependencies.copy()
        )
    
    def _convert_path_parameters(self, flask_path: str) -> str:
        """Convert Flask path parameters to FastAPI format"""
        # Convert <param> to {param}
        fastapi_path = re.sub(r'<([^>]+)>', r'{\\1}', flask_path)
        
        # Handle typed parameters <int:param> -> {param: int}
        fastapi_path = re.sub(r'<(int|float|string):([^>]+)>', r'{\\2}', fastapi_path)
        
        return fastapi_path
    
    def _convert_function_to_async(self, flask_route: FlaskRoute) -> str:
        """Convert Flask function to async FastAPI function"""
        
        lines = flask_route.function_code.split('\\n')
        converted_lines = []
        
        for line in lines:
            # Skip Flask decorator
            if '@app.route' in line:
                continue
            
            # Convert function definition to async
            if line.strip().startswith('def '):
                line = line.replace('def ', 'async def ')
            
            # Convert Flask imports
            line = self._convert_imports(line)
            
            # Convert request handling
            line = self._convert_request_handling(line)
            
            # Convert response handling
            line = self._convert_response_handling(line)
            
            converted_lines.append(line)
        
        return '\\n'.join(converted_lines)
    
    def _convert_imports(self, line: str) -> str:
        """Convert Flask imports to FastAPI equivalents"""
        conversions = {
            'from flask import': 'from fastapi import',
            'jsonify': 'JSONResponse',
            'request': 'Request',
            'abort': 'HTTPException'
        }
        
        for flask_import, fastapi_import in conversions.items():
            line = line.replace(flask_import, fastapi_import)
        
        return line
    
    def _convert_request_handling(self, line: str) -> str:
        """Convert Flask request handling to FastAPI"""
        
        # Convert request.get_json() to dependency injection
        if 'request.get_json()' in line:
            line = line.replace('request.get_json()', 'request_data')
            if 'request_data' not in self.dependencies:
                self.dependencies.append('request_data: dict = Body(...)')
        
        # Convert request.args to query parameters
        if 'request.args.get(' in line:
            line = re.sub(
                r'request\\.args\\.get\\([\'"]([^\'"]+)[\'"]\\)',
                r'\\1: Optional[str] = Query(None)',
                line
            )
        
        return line
    
    def _convert_response_handling(self, line: str) -> str:
        """Convert Flask response handling to FastAPI"""
        
        # Convert jsonify() to return dict
        line = re.sub(r'return jsonify\\(([^)]+)\\)', r'return \\1', line)
        
        # Convert Flask abort() to HTTPException
        line = re.sub(
            r'abort\\((\\d+)\\)',
            r'raise HTTPException(status_code=\\1)',
            line
        )
        
        return line
    
    def _generate_pydantic_models(self, flask_route: FlaskRoute) -> List[str]:
        """Generate Pydantic models for request/response"""
        models = []
        
        # Analyze function to determine if models are needed
        if 'POST' in flask_route.methods or 'PUT' in flask_route.methods:
            model_name = f"{flask_route.function_name.title()}Request"
            model_code = f'''
class {model_name}(BaseModel):
    """Request model for {flask_route.function_name}"""
    # Add fields based on analysis of request.get_json() usage
    pass
'''
            models.append(model_code.strip())
        
        return models


# Helper functions for common migration patterns
def convert_flask_error_handler(handler_func: Callable) -> str:
    """Convert Flask error handler to FastAPI exception handler"""
    
    source = inspect.getsource(handler_func)
    
    # Extract error code
    error_pattern = r'@app\\.errorhandler\\((\\d+)\\)'
    error_match = re.search(error_pattern, source)
    
    if not error_match:
        return source
    
    error_code = error_match.group(1)
    
    # Convert to FastAPI exception handler
    converted = f'''
@app.exception_handler({error_code})
async def handle_{error_code}_error(request: Request, exc: HTTPException):
    """Handle {error_code} errors"""
    return JSONResponse(
        status_code={error_code},
        content={{"error": "Error message here"}}
    )
'''
    
    return converted.strip()


def convert_flask_middleware(middleware_func: Callable) -> str:
    """Convert Flask before_request/after_request to FastAPI middleware"""
    
    source = inspect.getsource(middleware_func)
    
    if '@app.before_request' in source:
        return '''
@app.middleware("http")
async def before_request_middleware(request: Request, call_next):
    """Convert Flask before_request to FastAPI middleware"""
    # Add your before request logic here
    response = await call_next(request)
    return response
'''
    
    elif '@app.after_request' in source:
        return '''
@app.middleware("http")
async def after_request_middleware(request: Request, call_next):
    """Convert Flask after_request to FastAPI middleware"""
    response = await call_next(request)
    # Add your after request logic here
    return response
'''
    
    return source


def analyze_flask_app(app_file_path: str) -> Dict[str, Any]:
    """Analyze a Flask application file and provide migration insights"""
    
    with open(app_file_path, 'r') as f:
        content = f.read()
    
    analysis = {
        "routes": [],
        "error_handlers": [],
        "middleware": [],
        "imports": [],
        "complexity_score": 0
    }
    
    # Find routes
    route_pattern = r'@app\\.route\\([\'"]([^\'"]*)[\'"].*?\\)\\s*def\\s+(\\w+)'
    routes = re.findall(route_pattern, content, re.DOTALL)
    analysis["routes"] = [{"path": path, "function": func} for path, func in routes]
    
    # Find error handlers
    error_pattern = r'@app\\.errorhandler\\((\\d+)\\)\\s*def\\s+(\\w+)'
    errors = re.findall(error_pattern, content)
    analysis["error_handlers"] = [{"code": code, "function": func} for code, func in errors]
    
    # Find before/after request handlers
    middleware_pattern = r'@app\\.(before_request|after_request)\\s*def\\s+(\\w+)'
    middleware = re.findall(middleware_pattern, content)
    analysis["middleware"] = [{"type": mw_type, "function": func} for mw_type, func in middleware]
    
    # Analyze imports
    import_pattern = r'from flask import ([^\\n]+)'
    imports = re.findall(import_pattern, content)
    analysis["imports"] = [imp.strip() for imp_line in imports for imp in imp_line.split(',')]
    
    # Calculate complexity score
    analysis["complexity_score"] = (
        len(analysis["routes"]) * 2 +
        len(analysis["error_handlers"]) * 1 +
        len(analysis["middleware"]) * 3 +
        len(analysis["imports"]) * 0.5
    )
    
    return analysis


def generate_migration_report(analysis: Dict[str, Any]) -> str:
    """Generate a migration complexity report"""
    
    report = f"""
Flask to FastAPI Migration Report
================================

Application Analysis:
- Routes found: {len(analysis['routes'])}
- Error handlers: {len(analysis['error_handlers'])}
- Middleware functions: {len(analysis['middleware'])}
- Flask imports: {len(analysis['imports'])}
- Complexity score: {analysis['complexity_score']:.1f}

Migration Complexity: {"Low" if analysis['complexity_score'] < 20 else "Medium" if analysis['complexity_score'] < 50 else "High"}

Routes to convert:
"""
    
    for route in analysis['routes']:
        report += f"  - {route['path']} -> {route['function']}()\\n"
    
    if analysis['error_handlers']:
        report += "\\nError handlers to convert:\\n"
        for handler in analysis['error_handlers']:
            report += f"  - HTTP {handler['code']} -> {handler['function']}()\\n"
    
    if analysis['middleware']:
        report += "\\nMiddleware to convert:\\n"
        for mw in analysis['middleware']:
            report += f"  - {mw['type']} -> {mw['function']}()\\n"
    
    report += """
Recommended Migration Steps:
1. Set up FastAPI project structure
2. Convert route decorators to FastAPI equivalents
3. Add Pydantic models for request/response validation
4. Convert synchronous functions to async
5. Implement FastAPI middleware
6. Add FastAPI exception handlers
7. Update imports and dependencies
8. Test converted endpoints
9. Performance testing and optimization
"""
    
    return report


# Example usage
if __name__ == "__main__":
    print("Flask to FastAPI Migration Helper")
    print("=" * 40)
    
    # Example: Analyze the Flask app from our examples
    try:
        flask_app_path = "src/flask_examples/basic_app.py"
        analysis = analyze_flask_app(flask_app_path)
        report = generate_migration_report(analysis)
        print(report)
    except FileNotFoundError:
        print("Flask example file not found. Run from book root directory.")
    except Exception as e:
        print(f"Analysis failed: {e}")
    
    print("\\n💡 This is a basic migration helper.")
    print("   For complex applications, manual review and testing is essential.")
'''