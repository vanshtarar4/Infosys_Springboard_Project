'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { Bell, Sun, Moon, User, LogOut, ChevronDown } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'
import { dropdownVariants } from '@/utils/animations'

export default function TopBar() {
    const { theme, toggleTheme } = useTheme()
    const { user, logout } = useAuth()
    const [showNotifications, setShowNotifications] = useState(false)
    const [showUserMenu, setShowUserMenu] = useState(false)
    const [notificationCount, setNotificationCount] = useState(0)

    const notificationRef = useRef<HTMLDivElement>(null)
    const userMenuRef = useRef<HTMLDivElement>(null)

    // Reset notification count when dropdown is opened (mark as seen)
    useEffect(() => {
        if (showNotifications && notificationCount > 0) {
            // Wait a moment for the dropdown to open, then reset count
            const timer = setTimeout(() => {
                setNotificationCount(0)
            }, 500)
            return () => clearTimeout(timer)
        }
    }, [showNotifications, notificationCount])

    // Close dropdowns when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
                setShowNotifications(false)
            }
            if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
                setShowUserMenu(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    return (
        <motion.header
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="sticky top-0 h-16 border-b border-border glass z-30 px-6"
        >
            <div className="h-full flex items-center justify-between">
                {/* Left: Breadcrumb / Page Title */}
                <div className="flex items-center gap-4">
                    <h2 className="text-xl font-semibold text-foreground">
                        Fraud Detection Platform
                    </h2>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center gap-3">
                    {/* System Status */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-card border border-border"
                    >
                        <motion.div
                            animate={{
                                scale: [1, 1.2, 1],
                                opacity: [1, 0.6, 1],
                            }}
                            transition={{
                                duration: 2,
                                repeat: Infinity,
                                ease: 'easeInOut',
                            }}
                            className="w-2 h-2 rounded-full bg-success status-live"
                        />
                        <span className="text-sm font-medium text-muted-foreground">Live</span>
                    </motion.div>

                    {/* Notifications */}
                    <div className="relative" ref={notificationRef}>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => {
                                setShowNotifications(!showNotifications)
                                setShowUserMenu(false)
                            }}
                            className="relative w-10 h-10 rounded-lg bg-card hover:bg-card-hover border border-border flex items-center justify-center transition-colors"
                        >
                            <Bell className="w-5 h-5 text-muted-foreground" />
                            {notificationCount > 0 && !showNotifications && (
                                <motion.span
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-primary text-primary-foreground text-[10px] font-bold flex items-center justify-center"
                                >
                                    {notificationCount}
                                </motion.span>
                            )}
                        </motion.button>

                        {/* Notifications Dropdown */}
                        <AnimatePresence>
                            {showNotifications && (
                                <motion.div
                                    initial="closed"
                                    animate="open"
                                    exit="closed"
                                    variants={dropdownVariants}
                                    style={{
                                        backgroundColor: theme === 'dark' ? 'hsl(222, 47%, 15%)' : 'hsl(210, 40%, 98%)',
                                    }}
                                    className="absolute right-0 mt-2 w-80 border border-border rounded-lg shadow-2xl overflow-hidden z-[100]"
                                >
                                    <div className="p-4 border-b border-border" style={{
                                        backgroundColor: theme === 'dark' ? 'hsl(222, 47%, 15%)' : 'hsl(210, 40%, 98%)'
                                    }}>
                                        <h3 className="font-semibold text-foreground">Notifications</h3>
                                    </div>
                                    <div className="max-h-96 overflow-y-auto" style={{
                                        backgroundColor: theme === 'dark' ? 'hsl(222, 47%, 15%)' : 'hsl(210, 40%, 98%)'
                                    }}>
                                        {notificationCount === 0 ? (
                                            <div className="p-8 text-center">
                                                <p className="text-sm text-muted-foreground">No new notifications</p>
                                            </div>
                                        ) : (
                                            // Placeholder for future real notifications
                                            <div className="p-4">
                                                <p className="text-sm text-muted-foreground">Notifications will appear here</p>
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Theme Toggle */}
                    <motion.button
                        whileHover={{ scale: 1.05, rotate: 180 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={toggleTheme}
                        className="w-10 h-10 rounded-lg bg-card hover:bg-card-hover border border-border flex items-center justify-center transition-colors"
                    >
                        <AnimatePresence mode="wait">
                            {theme === 'dark' ? (
                                <motion.div
                                    key="moon"
                                    initial={{ rotate: -180, opacity: 0 }}
                                    animate={{ rotate: 0, opacity: 1 }}
                                    exit={{ rotate: 180, opacity: 0 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <Moon className="w-5 h-5 text-primary" />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="sun"
                                    initial={{ rotate: -180, opacity: 0 }}
                                    animate={{ rotate: 0, opacity: 1 }}
                                    exit={{ rotate: 180, opacity: 0 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <Sun className="w-5 h-5 text-warning" />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.button>

                    {/* User Menu */}
                    <div className="relative" ref={userMenuRef}>
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                                setShowUserMenu(!showUserMenu)
                                setShowNotifications(false)
                            }}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card hover:bg-card-hover border border-border transition-colors"
                        >
                            <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                                <User className="w-4 h-4 text-primary-foreground" />
                            </div>
                            <span className="text-sm font-medium text-foreground">Admin</span>
                            <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${showUserMenu ? 'rotate-180' : ''
                                }`} />
                        </motion.button>

                        {/* User Dropdown */}
                        <AnimatePresence>
                            {showUserMenu && (
                                <motion.div
                                    initial="closed"
                                    animate="open"
                                    exit="closed"
                                    variants={dropdownVariants}
                                    style={{
                                        backgroundColor: theme === 'dark' ? 'hsl(222, 47%, 15%)' : 'hsl(210, 40%, 98%)'
                                    }}
                                    className="absolute right-0 mt-2 w-56 border border-border rounded-lg shadow-2xl overflow-hidden z-[100]"
                                >
                                    <div className="px-4 py-3 border-b border-border" style={{
                                        backgroundColor: theme === 'dark' ? 'hsl(222, 47%, 15%)' : 'hsl(210, 40%, 98%)'
                                    }}>
                                        <p className="text-sm font-semibold text-foreground capitalize">{user?.username || 'User'}</p>
                                        <p className="text-xs text-muted-foreground capitalize">{user?.role || 'Role'}</p>
                                    </div>
                                    <div className="p-2" style={{
                                        backgroundColor: theme === 'dark' ? 'hsl(222, 47%, 15%)' : 'hsl(210, 40%, 98%)'
                                    }}>
                                        <motion.button
                                            whileHover={{ x: 4 }}
                                            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-card-hover text-left transition-colors"
                                        >
                                            <User className="w-4 h-4 text-muted-foreground" />
                                            <span className="text-sm text-foreground">Profile</span>
                                        </motion.button>
                                        <motion.button
                                            whileHover={{ x: 4 }}
                                            onClick={() => {
                                                logout()
                                                setShowUserMenu(false)
                                            }}
                                            className="w-full flex items-center gap-3 px-4 py-2.5 text-danger hover:bg-danger/10 transition-colors"
                                        >
                                            <LogOut className="w-4 h-4" />
                                            <span className="text-sm font-medium">Logout</span>
                                        </motion.button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </motion.header>
    )
}
