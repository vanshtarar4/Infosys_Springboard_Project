'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { motion } from 'framer-motion'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, loading } = useAuth()
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        if (!loading && !isAuthenticated && pathname !== '/login') {
            router.push('/login')
        }
    }, [isAuthenticated, loading, pathname, router])

    // Show loading spinner while checking auth
    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full"
                />
            </div>
        )
    }

    // If not authenticated and not on login page, don't render
    if (!isAuthenticated && pathname !== '/login') {
        return null
    }

    return <>{children}</>
}
