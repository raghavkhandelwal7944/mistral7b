"use client"

import type React from "react"

import { useAuth } from "@/components/auth-provider"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, CheckCircle, Eye, EyeOff, Info, MessageSquare } from "lucide-react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()
  const searchParams = useSearchParams()
  const { apiError, isDemoMode } = useAuth()

  const signupSuccess = searchParams.get("signup") === "success"

  // Auto-fill demo credentials when in demo mode
  useEffect(() => {
    if (isDemoMode) {
      setEmail("")
      setPassword("")
    }
  }, [isDemoMode])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    if (isDemoMode) {
      console.log("[v0] Demo mode login")
      // Simulate successful login
      setTimeout(() => {
        router.push("/")
        setIsLoading(false)
      }, 1000)
      return
    }

    try {
      console.log("[v0] Attempting login to:", `${API_BASE_URL}/api/auth/login`)
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
        credentials: "include",
      })

      const data = await response.json()

      if (response.ok) {
        console.log("[v0] Login successful:", data)
        document.cookie = `session_token=${data.session_token}; path=/; max-age=${30 * 24 * 60 * 60}; SameSite=Lax`
        localStorage.setItem("user", JSON.stringify(data.user))
        router.push("/")
      } else {
        setError(data.detail || "Login failed")
      }
    } catch (err) {
      console.error("[v0] Login error:", err)
      setError("Network error. Please check if the backend server is running on " + API_BASE_URL)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-4">
        {signupSuccess && (
          <Alert className="border-green-200 bg-green-50 text-green-800">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription>
              <strong>Account created successfully!</strong> You can now sign in with your credentials.
            </AlertDescription>
          </Alert>
        )}

        {isDemoMode && (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p>
                  <strong>Demo Mode Active</strong>
                </p>
                <p>
                  Backend server not detected. You can explore the interface with demo data. Click "Sign in" to
                  continue.
                </p>
              </div>
            </AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader className="text-center">
            <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-6 h-6 text-primary-foreground" />
            </div>
            <CardTitle className="text-2xl">Welcome back</CardTitle>
            <CardDescription>
              {isDemoMode ? "Demo Mode - Sign in to explore" : "Sign in to your Men's Mental Health Chatbot account"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {apiError && !isDemoMode && (
              <Alert variant="destructive" className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <div className="space-y-2">
                    <p>{apiError}</p>
                    <p className="text-sm">
                      To fix this:
                      <br />
                      1. Run the Python backend:{" "}
                      <code className="bg-muted px-1 rounded">python scripts/auth_backend.py</code>
                      <br />
                      2. Or set NEXT_PUBLIC_API_URL in Project Settings if using a different URL
                    </p>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder={isDemoMode ? "" : "Enter your email"}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder={isDemoMode ? "password (pre-filled)" : "Enter your password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoading}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Signing in..." : isDemoMode ? "Enter Demo" : "Sign in"}
              </Button>
            </form>

            {!isDemoMode && (
              <div className="mt-6 text-center text-sm">
                <span className="text-muted-foreground">Don't have an account? </span>
                <Link href="/auth/signup" className="text-primary hover:underline">
                  Sign up
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
