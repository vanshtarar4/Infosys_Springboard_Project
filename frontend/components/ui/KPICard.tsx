'use client'

import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import { useEffect, useState } from 'react'
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'
import { cardHover } from '@/utils/animations'
import { formatNumber } from '@/utils/helpers'

interface KPICardProps {
    title: string
    value: number
    icon: LucideIcon
    trend?: {
        value: number
        isPositive?: boolean
    }
    format?: 'number' | 'currency' | 'percentage'
    color?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
    delay?: number
}

const colorClasses = {
    primary: 'from-primary/20 to-primary/5 border-primary/20',
    success: 'from-success/20 to-success/5 border-success/20',
    warning: 'from-warning/20 to-warning/5 border-warning/20',
    danger: 'from-danger/20 to-danger/5 border-danger/20',
    info: 'from-secondary/20 to-secondary/5 border-secondary/20',
}

const iconColorClasses = {
    primary: 'bg-primary/10 text-primary',
    success: 'bg-success/10 text-success',
    warning: 'bg-warning/10 text-warning',
    danger: 'bg-danger/10 text-danger',
    info: 'bg-secondary/10 text-secondary',
}

export default function KPICard({
    title,
    value,
    icon: Icon,
    trend,
    format = 'number',
    color = 'primary',
    delay = 0,
}: KPICardProps) {
    const count = useMotionValue(0)
    const rounded = useTransform(count, (latest) => Math.round(latest))
    const [displayValue, setDisplayValue] = useState(0)

    // Animate the count when value changes
    useEffect(() => {
        const controls = animate(count, value, {
            duration: 1.5,
            delay: delay,
            ease: 'easeOut',
        })

        return () => controls.stop()
    }, [value, count, delay])

    // Subscribe to motion value changes to update display
    useEffect(() => {
        const unsubscribe = rounded.on('change', (latest) => {
            setDisplayValue(latest)
        })

        return unsubscribe
    }, [rounded])

    const formatValue = (val: number) => {
        switch (format) {
            case 'currency':
                return `$${formatNumber(val)}`
            case 'percentage':
                return `${val.toFixed(1)}%`
            default:
                return formatNumber(val)
        }
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.4 }}
            variants={cardHover}
            whileHover="hover"
            whileTap="tap"
            className={`
        relative overflow-hidden rounded-xl border
        bg-gradient-to-br ${colorClasses[color]}
        p-6 glass backdrop-blur-sm
        cursor-pointer group
      `}
        >
            {/* Background Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-transparent to-background/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

            {/* Content */}
            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                            {title}
                        </p>
                    </div>
                    <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className={`
              w-12 h-12 rounded-lg flex items-center justify-center
              ${iconColorClasses[color]}
            `}
                    >
                        <Icon className="w-6 h-6" />
                    </motion.div>
                </div>

                {/* Value */}
                <div className="space-y-2">
                    <div className="text-3xl font-bold text-foreground">
                        {formatValue(displayValue)}
                    </div>

                    {/* Trend Indicator */}
                    {trend && (
                        <div className={`flex items-center gap-1 text-sm font-medium ${trend.isPositive ? 'text-success' : 'text-danger'
                            }`}>
                            {trend.isPositive ? (
                                <TrendingUp className="w-4 h-4" />
                            ) : (
                                <TrendingDown className="w-4 h-4" />
                            )}
                            <span>{Math.abs(trend.value).toFixed(1)}%</span>
                            <span className="text-muted-foreground text-xs ml-1">vs last period</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Glow Effect */}
            <div className="absolute -inset-px bg-gradient-to-r from-primary/0 via-primary/50 to-primary/0 opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500" />
        </motion.div>
    )
}
