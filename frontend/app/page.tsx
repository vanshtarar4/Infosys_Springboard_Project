'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  LayoutDashboard,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  Shield,
  Download,
  ArrowRight,
  Activity,
} from 'lucide-react'
import KPICard from '@/components/ui/KPICard'
import StatusBadge from '@/components/ui/StatusBadge'
import { staggerContainer, staggerItem, fadeIn } from '@/utils/animations'

interface Metrics {
  total_transactions: number
  fraud_count: number
  fraud_rate: number
  avg_amount: number
  avg_amount_fraud: number
  avg_amount_legit: number
}

const API_BASE_URL = 'http://localhost:8001'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      console.log('[Dashboard] Fetching metrics from:', `${API_BASE_URL}/api/metrics`)
      const response = await fetch(`${API_BASE_URL}/api/metrics`)
      const data = await response.json()
      console.log('[Dashboard] Received data:', data)

      if (data.success) {
        console.log('[Dashboard] Setting metrics:', data.metrics)
        setMetrics(data.metrics)
      } else {
        setError('Failed to load metrics')
      }
    } catch (err) {
      setError('Error connecting to API')
      console.error('[Dashboard] Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const downloadCSV = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/download/processed`)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'transactions_processed.csv'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download failed:', err)
      alert('Failed to download CSV')
    }
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

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md mx-auto mt-12 p-6 rounded-xl border border-danger/20 bg-danger/5"
      >
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="w-6 h-6 text-danger" />
          <h3 className="text-lg font-semibold text-foreground">Connection Error</h3>
        </div>
        <p className="text-muted-foreground mb-4">{error}</p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={fetchMetrics}
          className="w-full px-4 py-2 bg-danger text-white rounded-lg font-medium hover:bg-danger/90 transition-colors"
        >
          Retry Connection
        </motion.button>
      </motion.div>
    )
  }

  if (!metrics) return null

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Fraud Detection Dashboard
          </h1>
          <p className="text-muted-foreground">
            Real-time monitoring and analytics for transaction security
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={downloadCSV}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-md"
        >
          <Download className="w-4 h-4" />
          Export Data
        </motion.button>
      </motion.div>

      {/* KPI Cards */}
      <motion.div
        variants={staggerContainer}
        initial="initial"
        animate="animate"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <motion.div variants={staggerItem}>
          <KPICard
            title="Total Transactions"
            value={metrics.total_transactions}
            icon={LayoutDashboard}
            trend={{ value: 12.5, isPositive: true }}
            color="primary"
            delay={0}
          />
        </motion.div>

        <motion.div variants={staggerItem}>
          <KPICard
            title="Fraud Detected"
            value={metrics.fraud_count}
            icon={AlertTriangle}
            trend={{ value: -8.3, isPositive: true }}
            color="danger"
            delay={0.1}
          />
        </motion.div>

        <motion.div variants={staggerItem}>
          <KPICard
            title="Fraud Rate"
            value={metrics.fraud_rate}
            icon={TrendingUp}
            format="percentage"
            trend={{ value: -5.2, isPositive: true }}
            color="warning"
            delay={0.2}
          />
        </motion.div>

        <motion.div variants={staggerItem}>
          <KPICard
            title="Avg Transaction"
            value={metrics.avg_amount}
            icon={DollarSign}
            format="currency"
            trend={{ value: 3.8, isPositive: true }}
            color="success"
            delay={0.3}
          />
        </motion.div>

        <motion.div variants={staggerItem}>
          <KPICard
            title="Avg Fraud Amount"
            value={metrics.avg_amount_fraud}
            icon={Shield}
            format="currency"
            color="danger"
            delay={0.4}
          />
        </motion.div>

        <motion.div variants={staggerItem}>
          <KPICard
            title="Avg Legit Amount"
            value={metrics.avg_amount_legit}
            icon={Activity}
            format="currency"
            color="info"
            delay={0.5}
          />
        </motion.div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        variants={fadeIn}
        initial="initial"
        animate="animate"
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {/* Fraud Detection Lab */}
        <Link href="/fraud-detection">
          <motion.div
            whileHover={{ scale: 1.02, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="p-6 rounded-xl border border-border glass cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Fraud Detection Lab
            </h3>
            <p className="text-sm text-muted-foreground">
              Analyze transactions in real-time with AI-powered detection
            </p>
          </motion.div>
        </Link>

        {/* Live Alerts */}
        <Link href="/alerts">
          <motion.div
            whileHover={{ scale: 1.02, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="p-6 rounded-xl border border-border glass cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-danger/10 flex items-center justify-center group-hover:bg-danger/20 transition-colors">
                <AlertTriangle className="w-6 h-6 text-danger" />
              </div>
              <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-danger group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Live Alerts
            </h3>
            <p className="text-sm text-muted-foreground">
              Monitor real-time fraud alerts and suspicious activities
            </p>
          </motion.div>
        </Link>

        {/* Model Performance */}
        <Link href="/model-performance">
          <motion.div
            whileHover={{ scale: 1.02, y: -4 }}
            whileTap={{ scale: 0.98 }}
            className="p-6 rounded-xl border border-border glass cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-success/10 flex items-center justify-center group-hover:bg-success/20 transition-colors">
                <TrendingUp className="w-6 h-6 text-success" />
              </div>
              <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-success group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Model Performance
            </h3>
            <p className="text-sm text-muted-foreground">
              View ML model metrics, accuracy, and evaluation results
            </p>
          </motion.div>
        </Link>
      </motion.div>

      {/* System Status */}
      <motion.div
        variants={fadeIn}
        initial="initial"
        animate="animate"
        className="p-6 rounded-xl border border-border glass"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <div>
              <p className="text-sm font-medium text-foreground">API Status</p>
              <p className="text-xs text-muted-foreground">Online</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <div>
              <p className="text-sm font-medium text-foreground">ML Model</p>
              <p className="text-xs text-muted-foreground">Active</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <div>
              <p className="text-sm font-medium text-foreground">Database</p>
              <p className="text-xs text-muted-foreground">Connected</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <div>
              <p className="text-sm font-medium text-foreground">Monitoring</p>
              <p className="text-xs text-muted-foreground">Live</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
