"use client"

import { useAuth } from "@/components/auth-provider"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Edit2, Info, LogOut, Menu, MessageSquare, Moon, MoreHorizontal, Plus, Send, Sun, Trash2 } from "lucide-react"
import { useTheme } from "next-themes"
import { useEffect, useRef, useState } from "react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface Message {
  id: string
  content: string
  role: "user" | "assistant"
  created_at: string
}

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export default function ChatGPT() {
  const { user, logout, isDemoMode, apiError, isLoading } = useAuth()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isChatLoading, setIsChatLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [renamingConversation, setRenamingConversation] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState("")
  const [openDropdown, setOpenDropdown] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { theme, setTheme } = useTheme()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (user) {
      if (isDemoMode) {
        loadDemoConversations()
      } else {
        loadConversations()
      }
    }
  }, [user, isDemoMode])

  useEffect(() => {
    if (currentConversation) {
      if (isDemoMode) {
        loadDemoMessages(currentConversation)
      } else {
        loadMessages(currentConversation)
      }
    } else {
      setMessages([])
    }
  }, [currentConversation, isDemoMode])

  const loadDemoConversations = () => {
    const demoConversations = [
      {
        id: "demo-1",
        title: "Welcome to ChatGPT Clone",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: "demo-2",
        title: "How to set up the backend",
        created_at: new Date(Date.now() - 86400000).toISOString(),
        updated_at: new Date(Date.now() - 86400000).toISOString(),
      },
      {
        id: "demo-3",
        title: "AI Integration with Mistral",
        created_at: new Date(Date.now() - 172800000).toISOString(),
        updated_at: new Date(Date.now() - 172800000).toISOString(),
      },
    ]
    setConversations(demoConversations)
    // Auto-select first conversation
    if (!currentConversation) {
      setCurrentConversation("demo-1")
    }
  }

  const loadDemoMessages = (conversationId: string) => {
    if (conversationId === "demo-1") {
      setMessages([
        {
          id: "msg-1",
          content:
            "Hello! Welcome to the ChatGPT Clone demo. This is a fully functional interface that shows what your app will look like once connected to the backend.",
          role: "assistant",
          created_at: new Date().toISOString(),
        },
        {
          id: "msg-2",
          content: "What can this demo do?",
          role: "user",
          created_at: new Date().toISOString(),
        },
        {
          id: "msg-3",
          content:
            "This demo shows:\n• Complete ChatGPT-style interface\n• Dark/light theme switching\n• Conversation management\n• Message history\n• User authentication flow\n\nTo get real AI responses, connect the Python backend with your Hugging Face API key!",
          role: "assistant",
          created_at: new Date().toISOString(),
        },
      ])
    } else if (conversationId === "demo-2") {
      setMessages([
        {
          id: "msg-4",
          content: "How do I set up the backend?",
          role: "user",
          created_at: new Date().toISOString(),
        },
        {
          id: "msg-5",
          content:
            "To set up the backend:\n\n1. **Install MySQL** and create 'chatgpt_clone' database\n2. **Run database schema**: Execute `scripts/database_schema.sql`\n3. **Install Python deps**: `pip install -r scripts/requirements_auth.txt`\n4. **Get Hugging Face API key** for Mistral model access\n5. **Start server**: `python scripts/auth_backend.py`\n\nOnce running, the app will automatically switch from demo mode to live mode!",
          role: "assistant",
          created_at: new Date().toISOString(),
        },
      ])
    } else if (conversationId === "demo-3") {
      setMessages([
        {
          id: "msg-6",
          content: "Tell me about the AI integration",
          role: "user",
          created_at: new Date().toISOString(),
        },
        {
          id: "msg-7",
          content:
            "The AI integration uses:\n\n• **Mistral-Small-3.2-24B-Instruct** model via Hugging Face\n• **FastAPI backend** for handling requests\n• **MySQL database** for conversation storage\n• **Session-based authentication** for user management\n• **Real-time WebSocket** support for typing indicators\n\nYou can also integrate your own fine-tuned Mistral model by updating the backend configuration!",
          role: "assistant",
          created_at: new Date().toISOString(),
        },
      ])
    }
  }

  const loadConversations = async () => {
    try {
      console.log("[v0] Loading conversations from:", `${API_BASE_URL}/api/conversations`)
      const response = await fetch(`${API_BASE_URL}/api/conversations`, {
        credentials: "include",
      })
      if (response.ok) {
        const data = await response.json()
        setConversations(data)
        console.log("[v0] Loaded conversations:", data)
      }
    } catch (error) {
      console.log("[v0] Failed to load conversations, staying in demo mode")
    }
  }

  const loadMessages = async (conversationId: string) => {
    try {
      console.log("[v0] Loading messages for conversation:", conversationId)
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages`, {
        credentials: "include",
      })
      if (response.ok) {
        const data = await response.json()
        setMessages(data)
        console.log("[v0] Loaded messages:", data)
      }
    } catch (error) {
      console.log("[v0] Failed to load messages")
    }
  }

  const createNewConversation = async () => {
    if (isDemoMode) {
      const newConv = {
        id: `demo-${Date.now()}`,
        title: "New Chat",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      setConversations((prev) => [newConv, ...prev])
      setCurrentConversation(newConv.id)
      setMessages([])
      return
    }

    try {
      console.log("[v0] Creating new conversation")
      const response = await fetch(`${API_BASE_URL}/api/conversations`, {
        method: "POST",
        credentials: "include",
      })
      if (response.ok) {
        const newConv = await response.json()
        setConversations((prev) => [newConv, ...prev])
        setCurrentConversation(newConv.id)
        console.log("[v0] Created new conversation:", newConv)
      }
    } catch (error) {
      console.log("[v0] Failed to create conversation")
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !currentConversation) return

    setIsChatLoading(true)
    const messageContent = input.trim()
    setInput("")

    // Add user message immediately
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      content: messageContent,
      role: "user",
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])

    if (isDemoMode) {
      // Simulate AI response in demo mode
      setTimeout(() => {
        const aiMessage: Message = {
          id: `msg-${Date.now() + 1}`,
          content: `This is a demo response to: "${messageContent}"\n\nIn demo mode, responses are simulated. To get real AI responses powered by Mistral:\n\n1. Set up the Python backend\n2. Configure your Hugging Face API key\n3. The app will automatically switch to live mode\n\nTry asking about the setup process or explore the existing demo conversations!`,
          role: "assistant",
          created_at: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, aiMessage])
        setIsChatLoading(false)

        // Update conversation title if it's a new chat
        if (currentConversation.startsWith("demo-") && messageContent) {
          const title = messageContent.slice(0, 30) + (messageContent.length > 30 ? "..." : "")
          setConversations((prev) => prev.map((c) => (c.id === currentConversation ? { ...c, title } : c)))
        }
      }, 1500)
      return
    }

    try {
      console.log("[v0] Sending message to conversation:", currentConversation)
      const response = await fetch(`${API_BASE_URL}/api/conversations/${currentConversation}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: messageContent }),
        credentials: "include",
      })

      if (response.ok) {
        const data = await response.json()
        setMessages((prev) => [
          ...prev.slice(0, -1), // Remove the temporary user message
          {
            id: data.user_message.id,
            content: data.user_message.content,
            role: data.user_message.role,
            created_at: new Date().toISOString(),
          },
          {
            id: data.ai_message.id,
            content: data.ai_message.content,
            role: data.ai_message.role,
            created_at: new Date().toISOString(),
          },
        ])

        loadConversations()
        console.log("[v0] Message sent successfully:", data)
      }
    } catch (error) {
      console.log("[v0] Failed to send message")
    } finally {
      setIsChatLoading(false)
    }
  }

  const deleteConversation = async (conversationId: string) => {
    if (!confirm("Are you sure you want to delete this conversation?")) return

    if (isDemoMode) {
      setConversations((prev) => prev.filter((c) => c.id !== conversationId))
      if (currentConversation === conversationId) {
        setCurrentConversation(null)
        setMessages([])
      }
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}`, {
        method: "DELETE",
        credentials: "include",
      })
      if (response.ok) {
        setConversations((prev) => prev.filter((c) => c.id !== conversationId))
        if (currentConversation === conversationId) {
          setCurrentConversation(null)
          setMessages([])
        }
      }
    } catch (error) {
      console.log("[v0] Failed to delete conversation")
    }
  }

  const renameConversation = async (conversationId: string, newTitle: string) => {
    console.log("[v0] Renaming conversation:", conversationId, "to:", newTitle)
    if (!newTitle.trim()) {
      console.log("[v0] Empty title, canceling rename")
      setRenamingConversation(null)
      setRenameValue("")
      return
    }

    if (isDemoMode) {
      console.log("[v0] Demo mode: updating conversation title")
      setConversations((prev) => prev.map((c) => (c.id === conversationId ? { ...c, title: newTitle.trim() } : c)))
      setRenamingConversation(null)
      setRenameValue("")
      console.log("[v0] Demo rename completed")
      return
    }

    try {
      console.log("[v0] Making API call to rename conversation")
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle.trim() }),
        credentials: "include",
      })
      if (response.ok) {
        console.log("[v0] API rename successful")
        setConversations((prev) => prev.map((c) => (c.id === conversationId ? { ...c, title: newTitle.trim() } : c)))
      } else {
        console.log("[v0] API rename failed:", response.status)
      }
    } catch (error) {
      console.log("[v0] Failed to rename conversation:", error)
    }
    setRenamingConversation(null)
    setRenameValue("")
  }

  const handleRenameComplete = (conversationId: string) => {
    console.log("[v0] handleRenameComplete called with:", conversationId, "renameValue:", renameValue)
    const currentTitle = conversations.find((c) => c.id === conversationId)?.title
    console.log("[v0] Current title:", currentTitle)

    if (renameValue.trim() && renameValue.trim() !== currentTitle) {
      console.log("[v0] Calling renameConversation")
      renameConversation(conversationId, renameValue.trim())
    } else {
      console.log("[v0] No change needed, canceling rename")
      setRenamingConversation(null)
      setRenameValue("")
    }
  }

  const startRename = (conversationId: string, currentTitle: string) => {
    console.log("[v0] Starting rename for:", conversationId, "current title:", currentTitle)
    setRenamingConversation(conversationId)
    setRenameValue(currentTitle)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="w-6 h-6 text-primary-foreground" />
          </div>
          <p>Loading Men's Mental Health Chatbot...</p>
        </div>
      </div>
    )
  }

  if (!user && !isDemoMode) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="w-6 h-6 text-primary-foreground" />
          </div>
          <p>Redirecting to login...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background" onClick={() => setOpenDropdown(null)}>
      {/* Sidebar */}
      <div
        className={`${sidebarOpen ? "w-64" : "w-0"} transition-all duration-300 overflow-hidden bg-sidebar border-r border-sidebar-border flex flex-col h-screen fixed left-0 top-0 z-10`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-3 border-b border-sidebar-border flex-shrink-0">
          <Button
            onClick={createNewConversation}
            className="w-full justify-start gap-2 bg-sidebar-accent hover:bg-sidebar-accent/80 text-sidebar-accent-foreground mb-2"
          >
            <Plus className="w-4 h-4" />
            New chat
          </Button>

          <div className="flex items-center justify-between text-sm text-sidebar-foreground/60">
            <span>
              {user?.first_name} {user?.last_name}
              {isDemoMode && <span className="text-xs text-primary"> (Demo)</span>}
            </span>
            <Button variant="ghost" size="sm" onClick={logout} className="p-1 h-auto hover:bg-sidebar-accent">
              <LogOut className="w-3 h-3" />
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer hover:bg-sidebar-accent mb-1 relative ${
                  currentConversation === conv.id ? "bg-sidebar-accent" : ""
                }`}
              >
                <MessageSquare className="w-4 h-4 text-sidebar-foreground/60 flex-shrink-0" />

                {renamingConversation === conv.id ? (
                  <Input
                    value={renameValue}
                    onChange={(e) => {
                      console.log("[v0] Rename input changed:", e.target.value)
                      setRenameValue(e.target.value)
                    }}
                    onKeyDown={(e) => {
                      console.log("[v0] Key pressed in rename input:", e.key)
                      if (e.key === "Enter") {
                        e.preventDefault()
                        e.stopPropagation()
                        console.log("[v0] Enter pressed, renaming to:", renameValue)
                        handleRenameComplete(conv.id)
                      } else if (e.key === "Escape") {
                        console.log("[v0] Escape pressed, canceling rename")
                        setRenamingConversation(null)
                        setRenameValue("")
                      }
                    }}
                    className="flex-1 text-sm h-6 px-1 bg-background border border-border"
                    autoFocus
                    onFocus={(e) => e.target.select()}
                  />
                ) : (
                  <span
                    className="flex-1 text-sm text-sidebar-foreground truncate"
                    onClick={() => setCurrentConversation(conv.id)}
                  >
                    {conv.title}
                  </span>
                )}

                <div className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="opacity-0 group-hover:opacity-100 p-1 h-6 w-6 hover:bg-sidebar-accent/80"
                    onClick={(e) => {
                      e.stopPropagation()
                      console.log("[v0] Dropdown menu clicked for conversation:", conv.id)
                      setOpenDropdown(openDropdown === conv.id ? null : conv.id)
                    }}
                  >
                    <MoreHorizontal className="w-3 h-3" />
                  </Button>

                  {openDropdown === conv.id && (
                    <div className="absolute right-0 top-full mt-1 w-32 bg-popover border border-border rounded-md shadow-md z-50">
                      <div
                        className="px-3 py-2 text-sm cursor-pointer hover:bg-accent rounded-t-md flex items-center gap-2"
                        onClick={(e) => {
                          e.stopPropagation()
                          console.log("[v0] Rename clicked for:", conv.id)
                          startRename(conv.id, conv.title)
                          setOpenDropdown(null)
                        }}
                      >
                        <Edit2 className="w-3 h-3" />
                        Rename
                      </div>
                      <div
                        className="px-3 py-2 text-sm cursor-pointer hover:bg-accent rounded-b-md flex items-center gap-2 text-destructive"
                        onClick={(e) => {
                          e.stopPropagation()
                          console.log("[v0] Delete clicked for:", conv.id)
                          deleteConversation(conv.id)
                          setOpenDropdown(null)
                        }}
                      >
                        <Trash2 className="w-3 h-3" />
                        Delete
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className={`flex-1 flex flex-col ${sidebarOpen ? "ml-64" : "ml-0"} transition-all duration-300`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2">
              <Menu className="w-4 h-4" />
            </Button>
            <h1 className="text-lg font-semibold">
              Men's Mental Health Chatbot {isDemoMode && <span className="text-sm text-primary">(Demo Mode)</span>}
            </h1>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="p-2"
          >
            {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </Button>
        </div>

        {isDemoMode && apiError && (
          <div className="p-4 pb-0">
            <div className="bg-destructive text-destructive-foreground rounded-lg p-4">
              <Info className="h-4 w-4" />
              <p className="text-sm mt-2">{apiError}</p>
              <p className="text-sm mt-2">Try the demo conversations or create a new chat to explore the interface!</p>
            </div>
          </div>
        )}

        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mb-4">
                <MessageSquare className="w-6 h-6 text-primary-foreground" />
              </div>
              <h2 className="text-2xl font-semibold mb-2">How can I help you today?</h2>
              <p className="text-muted-foreground">
                {currentConversation
                  ? "Start a conversation by typing a message below."
                  : "Select a conversation from the sidebar or create a new chat."}
              </p>
              {isDemoMode && (
                <p className="text-sm text-primary mt-2">
                  Demo mode active - explore the sample conversations or create your own!
                </p>
              )}
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((message) => (
                <div key={message.id} className="flex gap-4">
                  <Avatar className="w-8 h-8 mt-1">
                    <AvatarFallback
                      className={message.role === "user" ? "bg-primary text-primary-foreground" : "bg-secondary"}
                    >
                      {message.role === "user" ? user?.first_name?.[0] || "U" : "AI"}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-2">
                    <div className="prose prose-sm max-w-none dark:prose-invert">
                      <p className="text-foreground whitespace-pre-wrap">{message.content}</p>
                    </div>
                  </div>
                </div>
              ))}

              {isChatLoading && (
                <div className="flex gap-4">
                  <Avatar className="w-8 h-8 mt-1">
                    <AvatarFallback className="bg-secondary">AI</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                      <div
                        className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      />
                      <div
                        className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t border-border">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={currentConversation ? "Message Men's Mental Health Chatbot..." : "Select a conversation first"}
                className="flex-1"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                disabled={isChatLoading || !currentConversation}
              />
              <Button
                onClick={sendMessage}
                disabled={!input.trim() || isChatLoading || !currentConversation}
                size="sm"
                className="px-3"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              {isDemoMode
                ? "Demo mode - responses are simulated. Connect backend for real AI."
                : "Men's Mental Health Chatbot can make mistakes. Check important info. ⏳ CPU-only model may take 2-5 minutes to respond."}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}