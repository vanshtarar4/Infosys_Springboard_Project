'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
    AlertTriangle,
    ArrowLeft,
    Filter,
    RefreshCw,
    Clock,
    User,
    Activity,
} from 'lucide-react'
import StatusBadge from '@/components/ui/StatusBadge'
import { formatRelativeTime } from '@/utils/helpers'
import { staggerContainer, staggerItem, fadeIn } from '@/utils/animations'

interface Alert {
    alert_id: number
    transaction_id: string
    customer_id: string
    risk_score: number
    severity: string
    status: string
    alert_message: string
    triggered_rules: string[]
    created_at: string
    alert_type: string
}

export default function AlertsPage() {
    const [alerts, setAlerts] = useState<Alert[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [filter, setFilter] = useState({
        severity: '',
        status: ''
    })

    const fetchAlerts = useCallback(async () => {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 30000)

        try {
            const params = new URLSearchParams()
            if (filter.severity) params.append('severity', filter.severity)
            if (filter.status) params.append('status', filter.status)

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
            const response = await fetch(`${apiUrl}/api/alerts?${params}`, {
                signal: controller.signal
            })

            clearTimeout(timeoutId)
            const data = await response.json()

            if (data.success) {
                setAlerts(data.alerts)
                setError('')
            } else {
                setError(data.error)
            }
        } catch (err: any) {
            clearTimeout(timeoutId)
            if (err.name === 'AbortError') {
                setError('Request timeout. Please try again.')
            } else {
                setError('Failed to fetch alerts')
            }
        } finally {
            setLoading(false)
        }
    }, [filter])

    useEffect(() => {
        fetchAlerts()
        const interval = setInterval(fetchAlerts, 10000)
        return () => clearInterval(interval)
    }, [fetchAlerts])

    const getRiskColor = (risk: number) => {
        if (risk >= 0.8) return 'text-danger'
        if (risk >= 0.6) return 'text-warning'
        if (risk >= 0.4) return 'text-yellow-500'
        return 'text-success'
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'NEW': return 'bg-danger'
            case 'INVESTIGATING': return 'bg-warning'
            case 'RESOLVED': return 'bg-success'
            case 'FALSE_POSITIVE': return 'bg-secondary'
            case 'CONFIRMED': return 'bg-purple-500'
            default: return 'bg-muted'
        }
    }

    // Calculate statistics
    const stats = {
        total: alerts.length,
        critical: alerts.filter(a => a.severity === 'CRITICAL').length,
        high: alerts.filter(a => a.severity === 'HIGH').length,
        medium: alerts.filter(a => a.severity === 'MEDIUM').length,
        low: alerts.filter(a => a.severity === 'LOW').length,
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full"
                />
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-danger/10 flex items-center justify-center">
                            <AlertTriangle className="w-6 h-6 text-danger" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-foreground">
                                Fraud Alerts Monitor
                            </h1>
                            <p className="text-muted-foreground">
                                Real-time fraud detection alerts • Auto-refresh every 10s
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card border border-border">
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
                            className="w-2 h-2 rounded-full bg-success"
                        />
                        <span className="text-sm font-medium">Live</span>
                    </div>
                </div>
            </motion.div>

            {/* Stats Bar */}
            <motion.div
                variants={staggerContainer}
                initial="initial"
                animate="animate"
                className="grid grid-cols-2 md:grid-cols-5 gap-4"
            >
                <motion.div variants={staggerItem} className="p-4 rounded-xl glass border border-border">
                    <div className="text-sm text-muted-foreground mb-1">Total Alerts</div>
                    <div className="text-2xl font-bold text-foreground">{stats.total}</div>
                </motion.div>
                <motion.div variants={staggerItem} className="p-4 rounded-xl glass border border-danger/20">
                    <div className="text-sm text-muted-foreground mb-1">Critical</div>
                    <div className="text-2xl font-bold text-danger">{stats.critical}</div>
                </motion.div>
                <motion.div variants={staggerItem} className="p-4 rounded-xl glass border border-warning/20">
                    <div className="text-sm text-muted-foreground mb-1">High</div>
                    <div className="text-2xl font-bold text-warning">{stats.high}</div>
                </motion.div>
                <motion.div variants={staggerItem} className="p-4 rounded-xl glass border border-yellow-500/20">
                    <div className="text-sm text-muted-foreground mb-1">Medium</div>
                    <div className="text-2xl font-bold text-yellow-500">{stats.medium}</div>
                </motion.div>
                <motion.div variants={staggerItem} className="p-4 rounded-xl glass border border-success/20">
                    <div className="text-sm text-muted-foreground mb-1">Low</div>
                    <div className="text-2xl font-bold text-success">{stats.low}</div>
                </motion.div>
            </motion.div>

            {/* Filters */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass rounded-xl border border-border p-4"
            >
                <div className="flex gap-4 items-end">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-foreground mb-2">
                            <Filter className="w-4 h-4 inline mr-2" />
                            Severity
                        </label>
                        <select
                            value={filter.severity}
                            onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none text-foreground cursor-pointer"
                        >
                            <option value="">All Severities</option>
                            <option value="CRITICAL">Critical</option>
                            <option value="HIGH">High</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="LOW">Low</option>
                        </select>
                    </div>
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-foreground mb-2">
                            Status
                        </label>
                        <select
                            value={filter.status}
                            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none text-foreground cursor-pointer"
                        >
                            <option value="">All Statuses</option>
                            <option value="NEW">New</option>
                            <option value="INVESTIGATING">Investigating</option>
                            <option value="RESOLVED">Resolved</option>
                            <option value="FALSE_POSITIVE">False Positive</option>
                        </select>
                    </div>
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={fetchAlerts}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </motion.button>
                </div>
            </motion.div>

            {/* Alerts Table */}
            {error ? (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-6 rounded-xl border border-danger/20 bg-danger/5 text-center"
                >
                    <AlertTriangle className="w-12 h-12 text-danger mx-auto mb-3" />
                    <p className="text-foreground font-medium mb-2">Error Loading Alerts</p>
                    <p className="text-muted-foreground text-sm">{error}</p>
                </motion.div>
            ) : alerts.length === 0 ? (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-12 rounded-xl glass border border-border text-center"
                >
                    <Activity className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                    <h3 className="text-lg font-semibold text-foreground mb-2">No Alerts Found</h3>
                    <p className="text-muted-foreground text-sm">
                        {filter.severity || filter.status ? 'Try adjusting your filters' : 'All transactions are looking good'}
                    </p>
                </motion.div>
            ) : (
                <motion.div
                    variants={fadeIn}
                    initial="initial"
                    animate="animate"
                    className="glass rounded-xl border border-border overflow-hidden"
                >
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="border-b border-border bg-muted/5">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                        Alert ID
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                        Customer
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                        Risk Score
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                        Severity
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                        Status
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                        Time
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                <AnimatePresence>
                                    {alerts.map((alert, index) => (
                                        <motion.tr
                                            key={alert.alert_id}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.05 }}
                                            whileHover={{ backgroundColor: 'hsl(var(--card-hover))' }}
                                            className="transition-colors cursor-pointer"
                                        >
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="text-sm font-medium text-foreground">
                                                    #{alert.alert_id}
                                                </div>
                                                <div className="text-xs text-muted-foreground">
                                                    {alert.transaction_id}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex items-center gap-2">
                                                    <User className="w-4 h-4 text-muted-foreground" />
                                                    <span className="text-sm text-foreground">{alert.customer_id}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className={`text-sm font-semibold ${getRiskColor(alert.risk_score)}`}>
                                                    {(alert.risk_score * 100).toFixed(0)}%
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <StatusBadge
                                                    status={alert.severity}
                                                    severity={alert.severity as any}
                                                    animate={alert.severity === 'CRITICAL' || alert.severity === 'HIGH'}
                                                    size="sm"
                                                />
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${alert.status === 'NEW' ? 'bg-danger/10 text-danger' :
                                                        alert.status === 'INVESTIGATING' ? 'bg-warning/10 text-warning' :
                                                            alert.status === 'RESOLVED' ? 'bg-success/10 text-success' :
                                                                'bg-muted/10 text-muted-foreground'
                                                    }`}>
                                                    {alert.status.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                                    <Clock className="w-4 h-4" />
                                                    {formatRelativeTime(alert.created_at)}
                                                </div>
                                            </td>
                                        </motion.tr>
                                    ))}
                                </AnimatePresence>
                            </tbody>
                        </table>
                    </div>
                </motion.div>
            )}
        </div>
    )
}
