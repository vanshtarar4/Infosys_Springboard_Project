'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '@/contexts/AuthContext'
import { Shield, User, Lock, AlertCircle } from 'lucide-react'

export default function LoginPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const { login } = useAuth()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            await login(username, password)
        } catch (err: any) {
            setError(err.message || 'Invalid username or password')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md"
            >
                {/* Logo & Title */}
                <div className="text-center mb-8">
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                        className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-primary/10 flex items-center justify-center"
                    >
                        <Shield className="w-10 h-10 text-primary" />
                    </motion.div>
                    <h1 className="text-3xl font-bold text-foreground mb-2">
                        SecureGuard
                    </h1>
                    <p className="text-muted-foreground">
                        AI Fraud Detection Platform
                    </p>
                </div>

                {/* Login Form */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="glass rounded-2xl p-8 border border-border shadow-xl"
                >
                    <h2 className="text-2xl font-semibold text-foreground mb-6">
                        Sign In
                    </h2>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-6 p-4 rounded-lg bg-danger/10 border border-danger/20 flex items-start gap-3"
                        >
                            <AlertCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-danger">{error}</p>
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Username */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Enter your username"
                                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                    required
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                    required
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {/* Submit Button */}
                        <motion.button
                            whileHover={{ scale: loading ? 1 : 1.02 }}
                            whileTap={{ scale: loading ? 1 : 0.98 }}
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 px-4 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                                        className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full"
                                    />
                                    Signing in...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </motion.button>
                    </form>

                    {/* Demo Credentials */}
                    <div className="mt-6 pt-6 border-t border-border">
                        <p className="text-xs text-muted-foreground mb-3 font-medium">
                            Demo Credentials:
                        </p>
                        <div className="space-y-2 text-xs">
                            <div className="flex items-center gap-2">
                                <code className="px-2 py-1 rounded bg-muted text-foreground">
                                    admin / admin123
                                </code>
                                <span className="text-muted-foreground">Administrator</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <code className="px-2 py-1 rounded bg-muted text-foreground">
                                    analyst / analyst123
                                </code>
                                <span className="text-muted-foreground">Analyst</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <code className="px-2 py-1 rounded bg-muted text-foreground">
                                    viewer / viewer123
                                </code>
                                <span className="text-muted-foreground">Viewer</span>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Footer */}
                <p className="text-center text-sm text-muted-foreground mt-6">
                    Enterprise-grade fraud detection powered by AI
                </p>
            </motion.div>
        </div>
    )
}
