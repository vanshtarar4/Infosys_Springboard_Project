'use client'

import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'
import {
    LayoutDashboard,
    Search,
    Bell,
    TrendingUp,
    CreditCard,
    BarChart3,
    Upload,
    Settings,
    ChevronLeft,
    ChevronRight,
    Shield,
    AlertTriangle,
} from 'lucide-react'
import { sidebarVariants } from '@/utils/animations'

const navItems = [
    { href: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/fraud-detection', icon: Search, label: 'Fraud Lab' },
    { href: '/alerts', icon: AlertTriangle, label: 'Alerts', badge: 0 },
    { href: '/model-performance', icon: TrendingUp, label: 'Performance' },
    { href: '/transactions', icon: CreditCard, label: 'Transactions' },
    { href: '/analytics', icon: BarChart3, label: 'Analytics' },
    { href: '/upload', icon: Upload, label: 'Upload' },
]

const bottomNavItems = [
    { href: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
    const [isCollapsed, setIsCollapsed] = useState(false)
    const [isMobile, setIsMobile] = useState(false)
    const pathname = usePathname()

    // Responsive: Auto-collapse on mobile
    useEffect(() => {
        const checkMobile = () => {
            const mobile = window.innerWidth < 768
            setIsMobile(mobile)
            if (mobile) {
                setIsCollapsed(true) // Auto-collapse on mobile
            }
        }

        checkMobile()
        window.addEventListener('resize', checkMobile)
        return () => window.removeEventListener('resize', checkMobile)
    }, [])

    return (
        <motion.aside
            initial="expanded"
            animate={isCollapsed ? 'collapsed' : 'expanded'}
            variants={sidebarVariants}
            className="fixed left-0 top-0 h-screen border-r border-border glass z-40 flex flex-col"
        >
            {/* Logo Section */}
            <div className="h-16 flex items-center justify-between px-4 border-b border-border">
                <div className="flex items-center gap-3 overflow-hidden">
                    <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6, ease: 'easeInOut' }}
                        className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center flex-shrink-0"
                    >
                        <Shield className="w-5 h-5 text-white" />
                    </motion.div>

                    <AnimatePresence>
                        {!isCollapsed && (
                            <motion.h1
                                initial={{ opacity: 0, width: 0 }}
                                animate={{ opacity: 1, width: 'auto' }}
                                exit={{ opacity: 0, width: 0 }}
                                transition={{ duration: 0.2 }}
                                className="text-lg font-bold text-gradient whitespace-nowrap"
                            >
                                SecureGuard
                            </motion.h1>
                        )}
                    </AnimatePresence>
                </div>

                <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="w-8 h-8 rounded-lg bg-card-hover hover:bg-muted flex items-center justify-center transition-colors"
                >
                    {isCollapsed ? (
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    ) : (
                        <ChevronLeft className="w-4 h-4 text-muted-foreground" />
                    )}
                </motion.button>
            </div>

            {/* Navigation Items */}
            <nav className="flex-1 overflow-y-auto scrollbar-hide py-4">
                <div className="space-y-1 px-3">
                    {navItems.map((item, index) => {
                        const isActive = pathname === item.href
                        const Icon = item.icon

                        return (
                            <Link key={item.href} href={item.href}>
                                <motion.div
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    whileHover={{ x: 4 }}
                                    className={`
                    relative flex items-center gap-3 px-3 py-2.5 rounded-lg
                    transition-all duration-200 cursor-pointer group
                    ${isActive
                                            ? 'bg-primary text-primary-foreground shadow-glow'
                                            : 'text-muted-foreground hover:bg-card-hover hover:text-foreground'
                                        }
                  `}
                                >
                                    {/* Active Indicator */}
                                    {isActive && (
                                        <motion.div
                                            layoutId="activeIndicator"
                                            className="absolute inset-0 bg-primary rounded-lg"
                                            initial={false}
                                            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                                        />
                                    )}

                                    {/* Icon */}
                                    <Icon className={`w-5 h-5 flex-shrink-0 relative z-10 ${isActive ? 'text-primary-foreground' : ''
                                        }`} />

                                    {/* Label */}
                                    <AnimatePresence>
                                        {!isCollapsed && (
                                            <motion.span
                                                initial={{ opacity: 0, width: 0 }}
                                                animate={{ opacity: 1, width: 'auto' }}
                                                exit={{ opacity: 0, width: 0 }}
                                                transition={{ duration: 0.2 }}
                                                className={`text-sm font-medium whitespace-nowrap relative z-10 ${isActive ? 'text-primary-foreground' : ''
                                                    }`}
                                            >
                                                {item.label}
                                            </motion.span>
                                        )}
                                    </AnimatePresence>

                                    {/* Badge */}
                                    {item.badge !== undefined && item.badge > 0 && (
                                        <AnimatePresence>
                                            {!isCollapsed && (
                                                <motion.span
                                                    initial={{ opacity: 0, scale: 0.5 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    exit={{ opacity: 0, scale: 0.5 }}
                                                    className="ml-auto px-2 py-0.5 text-xs font-semibold bg-danger text-white rounded-full relative z-10"
                                                >
                                                    {item.badge}
                                                </motion.span>
                                            )}
                                        </AnimatePresence>
                                    )}

                                    {/* Tooltip for collapsed state */}
                                    {isCollapsed && (
                                        <div className="absolute left-full ml-2 px-2 py-1 bg-card border border-border rounded-md text-xs font-medium text-foreground whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                            {item.label}
                                            {item.badge !== undefined && item.badge > 0 && (
                                                <span className="ml-2 px-1.5 py-0.5 bg-danger text-white rounded-full text-[10px]">
                                                    {item.badge}
                                                </span>
                                            )}
                                        </div>
                                    )}
                                </motion.div>
                            </Link>
                        )
                    })}
                </div>
            </nav>

            {/* Bottom Navigation */}
            <div className="border-t border-border p-3">
                <div className="space-y-1">
                    {bottomNavItems.map((item) => {
                        const isActive = pathname === item.href
                        const Icon = item.icon

                        return (
                            <Link key={item.href} href={item.href}>
                                <motion.div
                                    whileHover={{ x: 4 }}
                                    className={`
                    relative flex items-center gap-3 px-3 py-2.5 rounded-lg
                    transition-all duration-200 cursor-pointer group
                    ${isActive
                                            ? 'bg-primary text-primary-foreground shadow-glow'
                                            : 'text-muted-foreground hover:bg-card-hover hover:text-foreground'
                                        }
                  `}
                                >
                                    <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-primary-foreground' : ''
                                        }`} />

                                    <AnimatePresence>
                                        {!isCollapsed && (
                                            <motion.span
                                                initial={{ opacity: 0, width: 0 }}
                                                animate={{ opacity: 1, width: 'auto' }}
                                                exit={{ opacity: 0, width: 0 }}
                                                transition={{ duration: 0.2 }}
                                                className={`text-sm font-medium whitespace-nowrap ${isActive ? 'text-primary-foreground' : ''
                                                    }`}
                                            >
                                                {item.label}
                                            </motion.span>
                                        )}
                                    </AnimatePresence>

                                    {isCollapsed && (
                                        <div className="absolute left-full ml-2 px-2 py-1 bg-card border border-border rounded-md text-xs font-medium text-foreground whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                            {item.label}
                                        </div>
                                    )}
                                </motion.div>
                            </Link>
                        )
                    })}
                </div>
            </div>
        </motion.aside>
    )
}
