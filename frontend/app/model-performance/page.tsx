'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
    TrendingUp,
    ArrowLeft,
    Target,
    CheckCircle,
    XCircle,
    AlertTriangle,
    Activity,
} from 'lucide-react'
import KPICard from '@/components/ui/KPICard'
import { staggerContainer, staggerItem, fadeIn } from '@/utils/animations'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function ModelPerformancePage() {
    const [metrics, setMetrics] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        fetchMetrics()
    }, [])

    const fetchMetrics = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/model/metrics`)
            const data = await response.json()

            if (data.success) {
                setMetrics(data.metrics)
            } else {
                setError(data.error)
            }
        } catch (err) {
            setError('Failed to load metrics')
        } finally {
            setLoading(false)
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
                    Retry
                </motion.button>
            </motion.div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-success" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-foreground">
                            Model Performance
                        </h1>
                        <p className="text-muted-foreground">
                            {metrics?.model_name || 'Fraud Detection Model'} • Threshold: {metrics?.threshold || 0.5}
                        </p>
                    </div>
                </div>
            </motion.div>

            {/* Core Metrics KPI Cards */}
            <motion.div
                variants={staggerContainer}
                initial="initial"
                animate="animate"
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6"
            >
                <motion.div variants={staggerItem}>
                    <KPICard
                        title="Accuracy"
                        value={metrics?.accuracy ? metrics.accuracy * 100 : 0}
                        icon={Target}
                        format="percentage"
                        color="info"
                        delay={0}
                    />
                </motion.div>
                <motion.div variants={staggerItem}>
                    <KPICard
                        title="Precision"
                        value={metrics?.precision ? metrics.precision * 100 : 0}
                        icon={CheckCircle}
                        format="percentage"
                        color="primary"
                        delay={0.1}
                    />
                </motion.div>
                <motion.div variants={staggerItem}>
                    <KPICard
                        title="Recall"
                        value={metrics?.recall ? metrics.recall * 100 : 0}
                        icon={Activity}
                        format="percentage"
                        color="success"
                        delay={0.2}
                    />
                </motion.div>
                <motion.div variants={staggerItem}>
                    <KPICard
                        title="F1-Score"
                        value={metrics?.f1_score ? metrics.f1_score * 100 : 0}
                        icon={TrendingUp}
                        format="percentage"
                        color="warning"
                        delay={0.3}
                    />
                </motion.div>
                <motion.div variants={staggerItem}>
                    <KPICard
                        title="ROC-AUC"
                        value={metrics?.roc_auc ? metrics.roc_auc * 100 : 0}
                        icon={CheckCircle}
                        format="percentage"
                        color="primary"
                        delay={0.4}
                    />
                </motion.div>
            </motion.div>

            {/* Fraud Detection & Confusion Matrix Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Fraud Detection Stats */}
                {metrics?.fraud_detection && (
                    <motion.div
                        variants={fadeIn}
                        initial="initial"
                        animate="animate"
                        className="glass rounded-xl border border-border p-6"
                    >
                        <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-primary" />
                            Fraud Detection Performance
                        </h2>

                        <div className="space-y-4">
                            {/* Detection Rate */}
                            <div className="p-4 rounded-lg bg-success/5 border border-success/20">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-muted-foreground">Detection Rate</span>
                                    <span className="text-2xl font-bold text-success">
                                        {(metrics.fraud_detection.detection_rate * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>

                            {/* Detected vs Missed Grid */}
                            <div className="grid grid-cols-2 gap-4">
                                {/* Frauds Detected */}
                                <motion.div
                                    whileHover={{ scale: 1.02 }}
                                    className="p-4 rounded-lg bg-success/10 border border-success/30"
                                >
                                    <div className="text-3xl font-bold text-success">
                                        {metrics.fraud_detection.frauds_detected}
                                    </div>
                                    <div className="text-xs text-muted-foreground mt-1">Frauds Detected</div>
                                </motion.div>

                                {/* Frauds Missed */}
                                <motion.div
                                    whileHover={{ scale: 1.02 }}
                                    className="p-4 rounded-lg bg-danger/10 border border-danger/30"
                                >
                                    <div className="text-3xl font-bold text-danger">
                                        {metrics.fraud_detection.frauds_missed}
                                    </div>
                                    <div className="text-xs text-muted-foreground mt-1">Frauds Missed</div>
                                </motion.div>
                            </div>

                            {/* Total Fraud Cases */}
                            <div className="p-4 rounded-lg bg-card border border-border">
                                <div className="text-sm text-muted-foreground mb-2">Total Fraud Cases</div>
                                <div className="text-2xl font-semibold text-foreground">
                                    {metrics.fraud_detection.total_fraud_cases}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Confusion Matrix */}
                {metrics?.confusion_matrix && (
                    <motion.div
                        variants={fadeIn}
                        initial="initial"
                        animate="animate"
                        transition={{ delay: 0.1 }}
                        className="glass rounded-xl border border-border p-6"
                    >
                        <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center gap-2">
                            <Target className="w-5 h-5 text-primary" />
                            Confusion Matrix
                        </h2>

                        <div className="grid grid-cols-2 gap-4">
                            {/* True Negatives */}
                            <motion.div
                                whileHover={{ scale: 1.05, y: -4 }}
                                className="p-6 rounded-xl bg-success/10 border-2 border-success/40 text-center"
                            >
                                <div className="text-4xl font-bold text-success mb-2">
                                    {metrics.confusion_matrix.true_negatives}
                                </div>
                                <div className="text-sm font-medium text-foreground">True Negatives</div>
                                <div className="text-xs text-muted-foreground mt-1">Correctly predicted legit</div>
                            </motion.div>

                            {/* False Positives */}
                            <motion.div
                                whileHover={{ scale: 1.05, y: -4 }}
                                className="p-6 rounded-xl bg-warning/10 border-2 border-warning/40 text-center"
                            >
                                <div className="text-4xl font-bold text-warning mb-2">
                                    {metrics.confusion_matrix.false_positives}
                                </div>
                                <div className="text-sm font-medium text-foreground">False Positives</div>
                                <div className="text-xs text-muted-foreground mt-1">False alarms</div>
                            </motion.div>

                            {/* False Negatives */}
                            <motion.div
                                whileHover={{ scale: 1.05, y: -4 }}
                                className="p-6 rounded-xl bg-danger/10 border-2 border-danger/40 text-center"
                            >
                                <div className="text-4xl font-bold text-danger mb-2">
                                    {metrics.confusion_matrix.false_negatives}
                                </div>
                                <div className="text-sm font-medium text-foreground">False Negatives</div>
                                <div className="text-xs text-muted-foreground mt-1">Missed fraud</div>
                            </motion.div>

                            {/* True Positives */}
                            <motion.div
                                whileHover={{ scale: 1.05, y: -4 }}
                                className="p-6 rounded-xl bg-success/10 border-2 border-success/40 text-center"
                            >
                                <div className="text-4xl font-bold text-success mb-2">
                                    {metrics.confusion_matrix.true_positives}
                                </div>
                                <div className="text-sm font-medium text-foreground">True Positives</div>
                                <div className="text-xs text-muted-foreground mt-1">Correctly caught fraud</div>
                            </motion.div>
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Metrics Comparison Progress Bars */}
            <motion.div
                variants={fadeIn}
                initial="initial"
                animate="animate"
                transition={{ delay: 0.2 }}
                className="glass rounded-xl border border-border p-6"
            >
                <h2 className="text-xl font-semibold text-foreground mb-6">Metrics Comparison</h2>

                <div className="space-y-5">
                    {['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc'].map((key, idx) => (
                        <motion.div
                            key={key}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.3 + idx * 0.1 }}
                            className="space-y-2"
                        >
                            <div className="flex justify-between text-sm">
                                <span className="capitalize text-foreground font-medium">
                                    {key.replace('_', ' ')}
                                </span>
                                <span className="font-semibold text-primary">
                                    {(metrics[key] * 100).toFixed(1)}%
                                </span>
                            </div>
                            <div className="w-full bg-muted/20 rounded-full h-3 overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${metrics[key] * 100}%` }}
                                    transition={{ duration: 1, delay: 0.5 + idx * 0.1, ease: 'easeOut' }}
                                    className={`h-full ${key === 'recall' ? 'bg-success' : 'bg-primary'
                                        }`}
                                />
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Note */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1 }}
                    className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-lg"
                >
                    <p className="text-sm text-foreground">
                        <strong>Note:</strong> This model is optimized for{' '}
                        <strong className="text-success">recall</strong> (catching fraud) over precision
                        (minimizing false alarms), which is appropriate for fraud detection use cases.
                    </p>
                </motion.div>
            </motion.div>
        </div>
    )
}
