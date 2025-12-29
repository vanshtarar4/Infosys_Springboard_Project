import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Merges Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

/**
 * Format number with commas
 */
export function formatNumber(num: number): string {
    return new Intl.NumberFormat('en-US').format(num)
}

/**
 * Format currency
 */
export function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount)
}

/**
 * Format percentage
 */
export function formatPercentage(value: number, decimals: number = 1): string {
    return `${value.toFixed(decimals)}%`
}

/**
 * Format relative time (e.g., "2 minutes ago")
 */
export function formatRelativeTime(date: Date | string): string {
    const now = new Date()
    const past = new Date(date)
    const diffInSeconds = Math.floor((now.getTime() - past.getTime()) / 1000)

    if (diffInSeconds < 60) return `${diffInSeconds}s ago`
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    return `${Math.floor(diffInSeconds / 86400)}d ago`
}

/**
 * Get risk severity based on score
 */
export function getRiskSeverity(score: number): 'low' | 'medium' | 'high' | 'critical' {
    if (score >= 0.9) return 'critical'
    if (score >= 0.7) return 'high'
    if (score >= 0.5) return 'medium'
    return 'low'
}

/**
 * Get color class for risk score
 */
export function getRiskColor(score: number): string {
    if (score >= 0.8) return 'text-red-500'
    if (score >= 0.6) return 'text-orange-500'
    if (score >= 0.4) return 'text-yellow-500'
    return 'text-green-500'
}

/**
 * Get background color class for severity
 */
export function getSeverityColor(severity: string): string {
    switch (severity.toUpperCase()) {
        case 'CRITICAL':
            return 'bg-red-500/10 text-red-500 border-red-500/20'
        case 'HIGH':
            return 'bg-orange-500/10 text-orange-500 border-orange-500/20'
        case 'MEDIUM':
            return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
        case 'LOW':
            return 'bg-green-500/10 text-green-500 border-green-500/20'
        default:
            return 'bg-muted/10 text-muted-foreground border-border'
    }
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout | null = null

    return function executedFunction(...args: Parameters<T>) {
        const later = () => {
            timeout = null
            func(...args)
        }

        if (timeout) clearTimeout(timeout)
        timeout = setTimeout(later, wait)
    }
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
): (...args: Parameters<T>) => void {
    let inThrottle: boolean

    return function executedFunction(...args: Parameters<T>) {
        if (!inThrottle) {
            func(...args)
            inThrottle = true
            setTimeout(() => (inThrottle = false), limit)
        }
    }
}
