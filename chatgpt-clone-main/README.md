# ChatGPT Clone with Mistral-7B Mental Health Model Integration

A full-stack ChatGPT-style web application featuring user authentication, conversation management, and integration with your deployed Mistral-7B mental health counseling model.

## 🌟 Features

- **Modern Next.js 14 Frontend**: React 18, TypeScript, Tailwind CSS 4
- **User Authentication**: Secure signup/login with session management
- **Conversation Management**: Create, rename, delete conversations
- **Chat Interface**: ChatGPT-style UI with message history
- **Dark/Light Theme**: Toggle between themes
- **AI Integration**: Connected to your deployed Mistral-7B model at `http://35.238.200.49:8000/chat`
- **MySQL Database**: Store users, conversations, and messages
- **FastAPI Backend**: Python backend handling auth and AI requests

## 📋 Prerequisites

Before setting up the application, ensure you have:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **MySQL** (v8.0 or higher) - [Download here](https://dev.mysql.com/downloads/mysql/)
- **Python** (v3.8 or higher) - [Download here](https://www.python.org/downloads/)
- **npm** or **pnpm** - Package manager for Node.js

## 🚀 Quick Start

### Step 1: Database Setup

1. **Install MySQL** (if not already installed)

2. **Start MySQL service**:
   ```bash
   # Windows (in Administrator Command Prompt)
   net start MySQL80
   
   # Or use MySQL Workbench/Services application
   ```

3. **Create database and tables**:
   ```bash
   # Connect to MySQL
   mysql -u root -p
   
   # Inside MySQL prompt, run the schema file (NO quotes around path):
   source c:/Users/raghav khandelwal/Desktop/mistral7b/chatgpt-clone-main/scripts/database_schema.sql
   
   # Or copy-paste the SQL commands from database_schema.sql
   ```

4. **Create MySQL user** (optional, recommended for security):
   ```sql
   CREATE USER 'Resilio_user'@'localhost' IDENTIFIED BY 'Rahulsoni@18';
   GRANT ALL PRIVILEGES ON resilio_db.* TO 'Resilio_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Step 2: Python Backend Setup

1. **Navigate to scripts directory**:
   ```bash
   cd "c:\Users\raghav khandelwal\Desktop\mistral7b\chatgpt-clone-main\scripts"
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements_auth.txt
   ```

3. **Configure environment variables** (optional):
   ```bash
   # Windows Command Prompt
   set MYSQL_HOST=localhost
   set MYSQL_USER=Resilio_user
   set MYSQL_PASSWORD=Rahulsoni@18
   set MYSQL_DATABASE=resilio_db
   set MYSQL_PORT=3306
   ```

4. **IMPORTANT: Integrate Your Deployed Mistral Model**
   
   The backend currently uses OpenAI/Groq APIs for AI responses. To use your deployed Mistral-7B model instead, modify `auth_backend.py`:

   **Find this function** (around line 340):
   ```python
   async def generate_ai_response(message: str) -> str:
       """Generate AI response using OpenAI API with Groq fallback"""
       
       # Try OpenAI first
       if OPENAI_API_KEY != 'your-openai-api-key-here':
           try:
               return await call_openai_api(message)
           except Exception as e:
               print(f"❌ OpenAI API Error: {str(e)}")
       
       # Try Groq as fallback
       if GROQ_API_KEY != 'your-groq-api-key-here':
           try:
               return await call_groq_api(message)
           except Exception as e:
               print(f"❌ Groq API Error: {str(e)}")
       
       # Fallback to demo response
       return f"I'm having trouble connecting..."
   ```

   **Replace it with this** (to use your deployed Mistral model):
   ```python
   async def generate_ai_response(message: str) -> str:
       """Generate AI response using deployed Mistral-7B model"""
       
       MISTRAL_API_URL = "http://35.238.200.49:8000/chat"
       
       try:
           payload = {"message": message}
           timeout = aiohttp.ClientTimeout(total=60)  # Increase timeout for model inference
           
           async with aiohttp.ClientSession(timeout=timeout) as session:
               async with session.post(MISTRAL_API_URL, json=payload) as response:
                   if response.status == 200:
                       result = await response.json()
                       return result.get('response', 'I apologize, but I could not generate a response.')
                   else:
                       error_text = await response.text()
                       print(f"❌ Mistral API Error [{response.status}]: {error_text}")
                       raise Exception(f"Mistral API returned {response.status}")
       
       except Exception as e:
           print(f"❌ Error calling Mistral API: {str(e)}")
           return "I'm having trouble connecting to the mental health counseling model right now. Please try again in a moment."
   ```

5. **Start the Python backend**:
   ```bash
   python auth_backend.py
   ```

   You should see:
   ```
   🚀 Starting Resilio Backend...
   ✅ Database tables initialized successfully
   🌐 Starting server on http://0.0.0.0:8000
   ```

   Keep this terminal running.

### Step 3: Frontend Setup

1. **Open a new terminal** and navigate to the chatgpt-clone-main folder:
   ```bash
   cd "c:\Users\raghav khandelwal\Desktop\mistral7b\chatgpt-clone-main"
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   # Or if you use pnpm:
   # pnpm install
   ```

3. **Configure environment variables**:
   
   Create a `.env.local` file in the `chatgpt-clone-main` folder:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

   You should see:
   ```
   ▲ Next.js 14.2.16
   - Local:        http://localhost:3000
   - Network:      http://192.168.x.x:3000
   
   ✓ Ready in 2.5s
   ```

5. **Open the application** in your browser:
   ```
   http://localhost:3000
   ```

## 🎯 Using the Application

### First-Time Setup

1. **Sign Up**: Click "Sign up" and create an account
   - Email: Your email address
   - Password: Your password
   - First Name & Last Name

2. **Login**: Use your credentials to log in

3. **Start Chatting**:
   - Click "New Chat" to create a conversation
   - Type your message and press Enter
   - The AI (your deployed Mistral-7B model) will respond
   - All conversations are saved to your account

### Features

- **Multiple Conversations**: Create unlimited chat conversations
- **Rename Conversations**: Click the pencil icon to rename
- **Delete Conversations**: Click the trash icon to delete
- **Theme Toggle**: Switch between dark and light modes
- **Message History**: All messages are saved in the database
- **Logout**: Click your profile icon → Logout

## 🔧 Configuration Options

### Database Configuration

Edit `auth_backend.py` (lines 22-28) or set environment variables:

```python
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'Resilio_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'Rahulsoni@18'),
    'database': os.getenv('MYSQL_DATABASE', 'resilio_db'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}
```

### API URL Configuration

The frontend connects to the backend via `NEXT_PUBLIC_API_URL`:

- **Development**: `http://localhost:8000` (default)
- **Production**: Change in `.env.local` file

### Mistral Model API

Your deployed model endpoint: `http://35.238.200.49:8000/chat`

**Request format**:
```json
{
  "message": "I'm feeling anxious about work"
}
```

**Response format**:
```json
{
  "response": "I understand that work-related anxiety can be challenging..."
}
```

## 📦 Project Structure

```
chatgpt-clone-main/
├── app/                          # Next.js app directory
│   ├── page.tsx                  # Main chat interface
│   ├── layout.tsx                # Root layout
│   ├── globals.css               # Global styles
│   └── auth/                     # Authentication pages
│       ├── login/page.tsx        # Login page
│       └── signup/page.tsx       # Signup page
├── components/                   # Reusable React components
│   ├── auth-provider.tsx         # Authentication context
│   ├── theme-provider.tsx        # Theme context
│   └── ui/                       # shadcn/ui components
├── scripts/                      # Backend Python scripts
│   ├── auth_backend.py           # FastAPI server (MODIFY THIS)
│   ├── database_schema.sql       # MySQL schema
│   └── requirements_auth.txt     # Python dependencies
├── package.json                  # Node.js dependencies
├── tsconfig.json                 # TypeScript config
└── README.md                     # This file
```

## 🛠️ Technology Stack

### Frontend
- **Next.js 14.2.16**: React framework with App Router
- **React 18**: UI library
- **TypeScript 5**: Type-safe JavaScript
- **Tailwind CSS 4.1.9**: Utility-first CSS framework
- **shadcn/ui**: Radix UI component library
- **Lucide React**: Icon library

### Backend
- **FastAPI**: Modern Python web framework
- **MySQL**: Relational database
- **bcrypt**: Password hashing
- **aiohttp**: Async HTTP client for API calls
- **Uvicorn**: ASGI server

### AI Model
- **Mistral-7B-Instruct-v0.3**: Base model
- **LoRA Fine-tuning**: Mental health counseling dataset
- **GCP Compute Engine**: Deployment (n1-standard-8, CPU-only)

## 🐛 Troubleshooting

### MySQL Connection Error

**Problem**: `Database error: Access denied for user...`

**Solution**:
1. Verify MySQL is running: `net start MySQL80`
2. Check credentials in `auth_backend.py`
3. Ensure user has correct privileges:
   ```sql
   GRANT ALL PRIVILEGES ON resilio_db.* TO 'Resilio_user'@'localhost';
   ```

### Backend Not Starting

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r scripts/requirements_auth.txt
```

### Frontend Not Connecting to Backend

**Problem**: Network errors in browser console

**Solution**:
1. Verify backend is running on `http://localhost:8000`
2. Check CORS settings in `auth_backend.py` (line 16):
   ```python
   allow_origins=["http://localhost:3000"]
   ```
3. Verify `.env.local` has correct API URL

### Mistral Model Not Responding

**Problem**: "I'm having trouble connecting..." message

**Solution**:
1. Verify your GCP VM is running and model server is active
2. Test the API directly:
   ```bash
   curl -X POST http://35.238.200.49:8000/chat ^
        -H "Content-Type: application/json" ^
        -d "{\"message\":\"Hello\"}"
   ```
3. Check if you modified `generate_ai_response()` function in `auth_backend.py`
4. Check backend terminal for error messages

### Port Already in Use

**Problem**: `Address already in use: 3000` or `8000`

**Solution**:
1. Frontend (port 3000):
   ```bash
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID_NUMBER> /F
   ```
2. Backend (port 8000):
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID_NUMBER> /F
   ```

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login and get session token
- `POST /api/auth/logout` - Logout and invalidate session
- `GET /api/auth/me` - Get current user info

### Conversation Endpoints

- `GET /api/conversations` - Get all user conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}/messages` - Get conversation messages
- `POST /api/conversations/{id}/messages` - Send message and get AI response
- `PATCH /api/conversations/{id}` - Update conversation title
- `DELETE /api/conversations/{id}` - Delete conversation

## 🚢 Production Deployment

### Backend Deployment

1. **Deploy to GCP/AWS/Azure**:
   - Use the same VM as your Mistral model or create a new one
   - Install dependencies: `pip install -r requirements_auth.txt`
   - Set environment variables for production database
   - Run with: `uvicorn auth_backend:app --host 0.0.0.0 --port 8000`

2. **Configure Firewall**:
   - Open port 8000 for API access
   - Ensure MySQL is accessible (port 3306)

### Frontend Deployment

1. **Build the Next.js app**:
   ```bash
   npm run build
   ```

2. **Deploy to Vercel** (recommended):
   - Connect your GitHub repo to Vercel
   - Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url.com`
   - Deploy automatically

3. **Update CORS in backend**:
   ```python
   allow_origins=["https://your-frontend-url.vercel.app"]
   ```

## 🔒 Security Considerations

- **Change default MySQL password** in production
- **Use HTTPS** for all API communication
- **Set secure session expiration** (currently 30 days)
- **Never commit** `.env.local` files to version control
- **Enable rate limiting** for API endpoints (optional)

## 📝 Next Steps

1. ✅ Set up MySQL database
2. ✅ Modify `auth_backend.py` to use your Mistral API
3. ✅ Start Python backend
4. ✅ Install frontend dependencies
5. ✅ Start frontend development server
6. ✅ Create account and start chatting
7. 🔄 Test with mental health related queries
8. 🚀 Deploy to production when ready

## 🤝 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check terminal logs for error messages
4. Ensure MySQL, backend, and frontend are all running

## 📄 License

This project uses:
- Next.js (MIT License)
- FastAPI (MIT License)
- Mistral-7B (Apache 2.0 License)

---

**Model API**: `http://35.238.200.49:8000/chat`  
**Backend API**: `http://localhost:8000`  
**Frontend**: `http://localhost:3000`  

🎉 **Happy Chatting with your Mental Health Counseling AI!**
