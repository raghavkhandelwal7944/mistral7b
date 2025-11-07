"use client"

import type React from "react"

import { usePathname, useRouter } from "next/navigation"
import { createContext, useContext, useEffect, useState } from "react"

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  logout: () => void
  apiError: string | null
  isDemoMode: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [apiError, setApiError] = useState<string | null>(null)
  const [isDemoMode, setIsDemoMode] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    checkAuth()
  }, [])

  const activateDemoMode = () => {
    console.log("[v0] Demo mode activated")
    setIsDemoMode(true)
    const demoUser = {
      id: 1,
      email: "demo@example.com",
      first_name: "Demo",
      last_name: "User",
    }
    setUser(demoUser)
    const isV0Preview =
      typeof window !== "undefined" &&
      (window.location.hostname.includes("v0.app") ||
        window.location.hostname.includes("vercel.app") ||
        window.location.hostname.includes("vusercontent.net"))

    if (isV0Preview) {
      setApiError(
        "🌐 You're viewing the v0 preview. To use your real Men's Mental Health Chatbot backend:\n\n" +
          "1️⃣ Download project: Click ⋯ → Download ZIP\n" +
          "2️⃣ Run backend: python scripts/auth_backend.py\n" +
          "3️⃣ Run frontend: npm run dev\n" +
          "4️⃣ Open: http://localhost:3000",
      )
    } else {
      setApiError(
        "⚠️ Backend not running. To connect real backend: 1) Run 'python scripts/auth_backend.py' 2) Refresh this page",
      )
    }
    setIsLoading(false)
  }

  const checkAuth = async () => {
    setIsLoading(true)

    const isV0Preview =
      typeof window !== "undefined" &&
      (window.location.hostname.includes("v0.app") ||
        window.location.hostname.includes("vercel.app") ||
        window.location.hostname.includes("vusercontent.net"))

    if (typeof window !== "undefined") {
      console.log("[v0] Environment check:", {
        hostname: window.location.hostname,
        port: window.location.port,
        isV0Preview,
        hasApiUrl: !!process.env.NEXT_PUBLIC_API_URL,
        apiBaseUrl: API_BASE_URL, // Added API URL to debug output
      })
    }

    // Only activate demo mode if actually in v0 preview environment
    if (isV0Preview && !process.env.NEXT_PUBLIC_API_URL) {
      console.log("[v0] Running in v0 preview - activating demo mode")
      activateDemoMode()
      return
    }

    const maxRetries = 3
    let lastError = null

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`[v0] Attempt ${attempt}/${maxRetries}: Connecting to backend:`, `${API_BASE_URL}/api/auth/me`)

        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 10000) // Increased timeout to 10 seconds

        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
          credentials: "include",
          signal: controller.signal,
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
        })

        clearTimeout(timeoutId)

        console.log("[v0] Backend connected! Response status:", response.status)
        setIsDemoMode(false)
        setApiError(null)

        if (response.ok) {
          const data = await response.json()
          console.log("[v0] User authenticated:", data.user.email)
          setUser(data.user)
          setIsLoading(false)
          if (pathname.startsWith("/auth")) {
            router.push("/")
          }
          return
        } else if (response.status === 401) {
          console.log("[v0] Backend connected, user not authenticated")
          setUser(null)
          setIsLoading(false)
          if (!pathname.startsWith("/auth")) {
            router.push("/auth/login")
          }
          return
        } else {
          console.log("[v0] Backend error:", response.status)
          lastError = `Backend error: ${response.status}`
          if (attempt === maxRetries) {
            setUser(null)
            setIsLoading(false)
            setApiError(lastError)
            return
          }
        }
      } catch (error) {
        console.log(`[v0] Attempt ${attempt} failed:`, error)
        lastError = error

        if (error instanceof Error && error.name === "AbortError") {
          console.log("[v0] Connection timeout")
          lastError = "Connection timeout"
        } else if (error instanceof TypeError && error.message.includes("fetch")) {
          console.log("[v0] Network error - backend may not be running")
          lastError = "Network error - backend not running"
        }

        if (attempt === maxRetries) {
          console.log("[v0] All connection attempts failed, activating demo mode")
          if (lastError === "Connection timeout") {
            setApiError("⏱️ Connection timeout. Make sure backend is running: python scripts/auth_backend.py")
          } else {
            setApiError("🔌 Cannot connect to backend. Start it with: python scripts/auth_backend.py")
          }
          activateDemoMode()
          return
        }

        await new Promise((resolve) => setTimeout(resolve, attempt * 1000))
      }
    }
  }

  const logout = async () => {
    if (isDemoMode) {
      setUser(null)
      setIsDemoMode(true)
      setApiError(null)
      router.push("/auth/login")
      return
    }

    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      })

      localStorage.removeItem("user")
      document.cookie = "session_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT"
      setUser(null)
      router.push("/auth/login")
    } catch (error) {
      console.log("[v0] Logout failed, switching to demo mode")
      localStorage.removeItem("user")
      document.cookie = "session_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT"
      activateDemoMode()
      router.push("/auth/login")
    }
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, logout, apiError, isDemoMode }}>{children}</AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
