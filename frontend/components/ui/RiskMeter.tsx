'use client'

import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import { useEffect, useState } from 'react'

interface RiskMeterProps {
    score: number // 0-100
    size?: number
    strokeWidth?: number
    delay?: number
}

export default function RiskMeter({
    score,
    size = 200,
    strokeWidth = 16,
    delay = 0
}: RiskMeterProps) {
    const progress = useMotionValue(0)
    const [displayValue, setDisplayValue] = useState(0)
    const circumference = 2 * Math.PI * (size / 2 - strokeWidth / 2)

    // Animated progress for the arc
    const pathLength = useTransform(progress, [0, 100], [0, 1])

    // Animated score display
    const displayScore = useTransform(progress, (latest) => Math.round(latest))

    // Animate progress when score changes
    useEffect(() => {
        const controls = animate(progress, score, {
            duration: 1.5,
            delay,
            ease: [0.4, 0.0, 0.2, 1],
        })

        return () => controls.stop()
    }, [score, progress, delay])

    // Subscribe to motion value changes for reactive display
    useEffect(() => {
        const unsubscribe = displayScore.on('change', (latest) => {
            setDisplayValue(latest)
        })

        return unsubscribe
    }, [displayScore])

    // Get color based on score
    const getColor = (value: number) => {
        if (value >= 80) return 'hsl(var(--danger))' // Red
        if (value >= 60) return 'hsl(var(--warning))' // Amber
        if (value >= 40) return 'hsl(38, 92%, 50%)' // Yellow
        return 'hsl(var(--success))' // Green
    }

    // Get severity label
    const getSeverity = (value: number) => {
        if (value >= 90) return 'CRITICAL'
        if (value >= 70) return 'HIGH'
        if (value >= 50) return 'MEDIUM'
        return 'LOW'
    }

    const radius = size / 2 - strokeWidth / 2
    const centerX = size / 2
    const centerY = size / 2

    return (
        <div className="flex flex-col items-center gap-4">
            {/* SVG Circle */}
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay, duration: 0.4 }}
                className="relative"
                style={{ width: size, height: size }}
            >
                <svg
                    width={size}
                    height={size}
                    className="transform -rotate-90"
                >
                    {/* Background Circle */}
                    <circle
                        cx={centerX}
                        cy={centerY}
                        r={radius}
                        fill="none"
                        stroke="hsl(var(--muted) / 0.2)"
                        strokeWidth={strokeWidth}
                    />

                    {/* Progress Arc */}
                    <motion.circle
                        cx={centerX}
                        cy={centerY}
                        r={radius}
                        fill="none"
                        stroke={getColor(displayValue)}
                        strokeWidth={strokeWidth}
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={useTransform(pathLength, [0, 1], [circumference, 0])}
                        style={{
                            filter: `drop-shadow(0 0 8px ${getColor(displayValue)})`,
                        }}
                    />
                </svg>

                {/* Center Content */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <motion.div className="text-5xl font-bold text-foreground tabular-nums">
                        {displayValue}%
                    </motion.div>
                    <p className="text-sm text-muted-foreground mt-1">Risk Score</p>
                </div>
            </motion.div>

            {/* Severity Badge */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: delay + 0.5, duration: 0.3 }}
                className={`
          px-4 py-2 rounded-full text-sm font-semibold
          ${score >= 90 ? 'bg-danger/10 text-danger border border-danger/20' :
                        score >= 70 ? 'bg-warning/10 text-warning border border-warning/20' :
                            score >= 50 ? 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20' :
                                'bg-success/10 text-success border border-success/20'}
        `}
            >
                {getSeverity(score)} RISK
            </motion.div>
        </div>
    )
}
