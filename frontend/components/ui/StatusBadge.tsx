'use client'

import { motion } from 'framer-motion'
import { getSeverityColor } from '@/utils/helpers'

interface StatusBadgeProps {
    status: string
    severity?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
    animate?: boolean
    size?: 'sm' | 'md' | 'lg'
}

const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
}

export default function StatusBadge({
    status,
    severity,
    animate = false,
    size = 'md'
}: StatusBadgeProps) {
    const severityLevel = severity || status
    const colorClass = getSeverityColor(severityLevel)

    const pulseAnimation = animate && (severity === 'CRITICAL' || severity === 'HIGH') ? {
        scale: [1, 1.05, 1],
        opacity: [1, 0.8, 1],
    } : {}

    const breathingAnimation = animate && severity === 'MEDIUM' ? {
        opacity: [1, 0.7, 1],
    } : {}

    return (
        <motion.span
            animate={{
                ...pulseAnimation,
                ...breathingAnimation,
            }}
            transition={{
                duration: severity === 'CRITICAL' ? 1.5 : 2,
                repeat: animate ? Infinity : 0,
                ease: 'easeInOut',
            }}
            className={`
        inline-flex items-center justify-center
        font-semibold rounded-full border
        ${colorClass}
        ${sizeClasses[size]}
        transition-all duration-200
      `}
        >
            {/* Status Dot for Critical/High */}
            {animate && (severity === 'CRITICAL' || severity === 'HIGH') && (
                <motion.span
                    animate={{
                        scale: [1, 1.5, 1],
                        opacity: [1, 0.5, 1],
                    }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: 'easeInOut',
                    }}
                    className="w-2 h-2 rounded-full bg-current mr-2"
                />
            )}
            {status}
        </motion.span>
    )
}
