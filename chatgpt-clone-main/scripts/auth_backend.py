import asyncio
import json
import os
import secrets
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Optional

import aiohttp
import bcrypt
import mysql.connector
from fastapi import Cookie, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mysql.connector import Error
from pydantic import BaseModel, EmailStr

app = FastAPI(title="men's mental health chatbot Auth API")
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'Resilio_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'TTLShiwwya1234...'),  # ← CHANGE HERE
    'database': os.getenv('MYSQL_DATABASE', 'resilio_db'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

print("🔍 Debug: Database configuration:")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   User: {DB_CONFIG['user']}")
print(f"   Database: {DB_CONFIG['database']}")
print(f"   Port: {DB_CONFIG['port']}")
print(f"   Password: {'*' * len(DB_CONFIG['password'])}")

env_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE', 'MYSQL_PORT']
print("🔍 Environment variables:")
for var in env_vars:
    value = os.getenv(var)
    if value:
        display_value = '*' * len(value) if 'PASSWORD' in var else value
        print(f"   {var}={display_value}")
    else:
        print(f"   {var}=<not set>")

# OpenAI API configuration
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

# Alternative: Groq API (faster and free tier available)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')

# Pydantic models
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime

class ChatMessage(BaseModel):
    content: str

class Message(BaseModel):
    id: str
    content: str
    role: str
    created_at: datetime

class Conversation(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

class ConversationUpdate(BaseModel):
    title: str

# Database connection context manager
@contextmanager
def get_db_connection():
    connection = None
    try:
        print(f"🔌 Attempting MySQL connection with: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✅ MySQL connection successful")
        yield connection
    except Error as e:
        print(f"❌ MySQL connection failed: {str(e)}")
        print(f"❌ Failed config: {DB_CONFIG}")
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            connection.close()

# Password hashing
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Session management
def create_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=30)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, user_id, expires_at) VALUES (%s, %s, %s)",
            (session_id, user_id, expires_at)
        )
        conn.commit()
    
    return session_id

def get_user_from_session(session_id: str) -> Optional[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id, u.email, u.first_name, u.last_name, u.created_at
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.id = %s AND s.expires_at > NOW()
        """, (session_id,))
        return cursor.fetchone()

def delete_session(session_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
        conn.commit()

# Dependency to get current user
async def get_current_user(session_token: Optional[str] = Cookie(None)) -> dict:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = get_user_from_session(session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return user

# Auth endpoints
@app.post("/api/auth/signup")
async def signup(user_data: UserSignup):
    hashed_password = hash_password(user_data.password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name)
                VALUES (%s, %s, %s, %s)
            """, (user_data.email, hashed_password, user_data.first_name, user_data.last_name))
            conn.commit()
            user_id = cursor.lastrowid
            
        session_id = create_session(user_id)
        
        return {
            "message": "User created successfully",
            "session_token": session_id,
            "user": {
                "id": user_id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name
            }
        }
    except mysql.connector.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, email, password_hash, first_name, last_name FROM users WHERE email = %s",
            (user_data.email,)
        )
        user = cursor.fetchone()
    
    if not user or not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    session_id = create_session(user['id'])
    
    return {
        "message": "Login successful",
        "session_token": session_id,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name']
        }
    }

@app.post("/api/auth/logout")
async def logout(session_token: Optional[str] = Cookie(None)):
    if session_token:
        delete_session(session_token)
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# Chat endpoints (protected)
@app.get("/api/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)) -> List[Conversation]:
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY updated_at DESC
        """, (current_user['id'],))
        conversations = cursor.fetchall()
    
    return conversations

@app.post("/api/conversations")
async def create_conversation(current_user: dict = Depends(get_current_user)):
    conversation_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (id, user_id, title)
            VALUES (%s, %s, %s)
        """, (conversation_id, current_user['id'], "New Chat"))
        conn.commit()
    
    return {"id": conversation_id, "title": "New Chat"}

@app.get("/api/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, current_user: dict = Depends(get_current_user)) -> List[Message]:
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        # Verify conversation belongs to user
        cursor.execute("""
            SELECT id FROM conversations
            WHERE id = %s AND user_id = %s
        """, (conversation_id, current_user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        cursor.execute("""
            SELECT id, content, role, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
        """, (conversation_id,))
        messages = cursor.fetchall()
    
    return messages

@app.post("/api/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    # Verify conversation belongs to user and get conversation history
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id FROM conversations
            WHERE id = %s AND user_id = %s
        """, (conversation_id, current_user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Retrieve conversation history (last 20 messages for context)
        cursor.execute("""
            SELECT content, role, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        conversation_history = cursor.fetchall()
        print(f"📜 Retrieved {len(conversation_history)} previous messages for context")
        
        # Save user message
        user_message_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO messages (id, conversation_id, content, role)
            VALUES (%s, %s, %s, %s)
        """, (user_message_id, conversation_id, message.content, "user"))
        
        # Update conversation timestamp
        cursor.execute("""
            UPDATE conversations SET updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (conversation_id,))
        conn.commit()
    
    # Generate AI response with conversation history for context
    ai_response = await generate_ai_response(message.content, conversation_history)
    
    # Save AI response
    with get_db_connection() as conn:
        cursor = conn.cursor()
        ai_message_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO messages (id, conversation_id, content, role)
            VALUES (%s, %s, %s, %s)
        """, (ai_message_id, conversation_id, ai_response, "assistant"))
        conn.commit()
    
    return {
        "user_message": {"id": user_message_id, "content": message.content, "role": "user"},
        "ai_message": {"id": ai_message_id, "content": ai_response, "role": "assistant"}
    }

@app.patch("/api/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    current_user: dict = Depends(get_current_user)
):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Verify conversation belongs to user
        cursor.execute("""
            SELECT id FROM conversations
            WHERE id = %s AND user_id = %s
        """, (conversation_id, current_user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update conversation title
        cursor.execute("""
            UPDATE conversations 
            SET title = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        """, (update_data.title, conversation_id, current_user['id']))
        conn.commit()
    
    return {"message": "Conversation updated successfully", "title": update_data.title}

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        
        # Verify conversation belongs to user
        cursor.execute("""
            SELECT id FROM conversations
            WHERE id = %s AND user_id = %s
        """, (conversation_id, current_user['id']))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete conversation (messages will be deleted automatically due to CASCADE)
        cursor.execute("""
            DELETE FROM conversations
            WHERE id = %s AND user_id = %s
        """, (conversation_id, current_user['id']))
        conn.commit()
    
    return {"message": "Conversation deleted successfully"}

async def generate_ai_response(message: str, conversation_history: List[dict] = None) -> str:
    """
    Generate AI response using deployed Mistral-7B model with conversation history.
    
    Args:
        message: Current user message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
    """
    
    MISTRAL_API_URL = "http://35.238.200.49:8000/chat"
    
    # Build context with last N messages (default: 10 exchanges = 20 messages)
    MAX_HISTORY_MESSAGES = 20  # Last 10 user + 10 assistant messages
    
    # Prepare conversation context
    context_messages = []
    if conversation_history:
        # Take only the last N messages to keep context manageable
        recent_history = conversation_history[-MAX_HISTORY_MESSAGES:]
        for msg in recent_history:
            context_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add current message
    context_messages.append({
        "role": "user",
        "content": message
    })
    
    # Format for Mistral model (if it supports conversation history)
    # Otherwise, concatenate into a single context string
    context_string = ""
    for msg in context_messages[:-1]:  # Exclude current message
        if msg["role"] == "user":
            context_string += f"User: {msg['content']}\n"
        else:
            context_string += f"Assistant: {msg['content']}\n"
    
    # Build final prompt with context
    if context_string:
        full_message = f"Previous conversation:\n{context_string}\nUser: {message}\nAssistant:"
    else:
        full_message = message
    
    try:
        payload = {"message": full_message}
        print(f"🔄 Calling Mistral API with context ({len(context_messages)-1} previous messages)...")
        print(f"⏳ CPU-only inference - this may take 5-10 minutes, please wait...")
        
        # CPU inference is VERY slow - give it 10 minutes
        timeout = aiohttp.ClientTimeout(total=600)  # 10 minutes for CPU-only model
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(MISTRAL_API_URL, json=payload) as response:
                print(f"📡 Mistral API responded with status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get('response', 'I apologize, but I could not generate a response.')
                    print(f"✅ Mistral API success: {ai_response[:100]}...")
                    return ai_response
                else:
                    error_text = await response.text()
                    print(f"❌ Mistral API Error [{response.status}]: {error_text}")
                    raise Exception(f"Mistral API returned {response.status}")
    
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Cannot connect to Mistral API - server may be down: {str(e)}")
        return "I'm having trouble connecting to the mental health counseling server. The server may be offline. Please check if your GCP VM is running and the FastAPI server is active on port 8000."
    except asyncio.TimeoutError:
        print(f"❌ Mistral API timeout - model inference took longer than 5 minutes")
        return "I apologize, but the response is taking too long (over 5 minutes). The model is running on CPU which is very slow. Please try asking a shorter, simpler question, or consider upgrading to a GPU instance for faster responses."
    except Exception as e:
        print(f"❌ Error calling Mistral API: {type(e).__name__} - {str(e)}")
        return "I'm having trouble connecting to the mental health counseling model right now. Please try again in a moment."
async def call_openai_api(message: str, conversation_history: List[dict] = None) -> str:
    """Call OpenAI API with conversation history"""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Build messages array with history
    messages = [
        {"role": "system", "content": "You are a men's mental health chatbot, a helpful AI assistant. Provide clear, concise, and supportive responses for men's mental health."}
    ]
    
    # Add conversation history (last 20 messages)
    if conversation_history:
        MAX_HISTORY = 20
        for msg in conversation_history[-MAX_HISTORY:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(OPENAI_API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                error_text = await response.text()
                raise Exception(f"OpenAI API returned {response.status}: {error_text}")

async def call_groq_api(message: str, conversation_history: List[dict] = None) -> str:
    """Call Groq API (faster alternative) with conversation history"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Build messages array with history
    messages = [
        {"role": "system", "content": "You are a men's mental health chatbot, a helpful AI assistant. Provide clear, concise, and supportive responses for men's mental health."}
    ]
    
    # Add conversation history (last 20 messages)
    if conversation_history:
        MAX_HISTORY = 20
        for msg in conversation_history[-MAX_HISTORY:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(GROQ_API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                error_text = await response.text()
                raise Exception(f"Groq API returned {response.status}: {error_text}")

# Database initialization and better error handling
def init_database():
    """Initialize database tables if they don't exist"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id INT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL DEFAULT 'New Chat',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id VARCHAR(255) PRIMARY KEY,
                    conversation_id VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    role ENUM('user', 'assistant') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            print("✅ Database tables initialized successfully")
            
    except Error as e:
        print(f"❌ Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Resilio Backend...")
    print(f"📊 Database Config: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    try:
        init_database()
        print("🌐 Starting server on http://0.0.0.0:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"💥 Failed to start server: {str(e)}")
        exit(1)