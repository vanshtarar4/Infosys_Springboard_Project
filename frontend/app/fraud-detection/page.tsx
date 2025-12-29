'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
    Shield,
    ArrowLeft,
    Loader2,
    AlertTriangle,
    TrendingDown,
    TrendingUp,
    Clock,
    User,
    DollarSign,
    Calendar,
    Globe,
    CheckCircle2,
    XCircle,
} from 'lucide-react'
import RiskMeter from '@/components/ui/RiskMeter'
import StatusBadge from '@/components/ui/StatusBadge'
import PageTransition from '@/components/layout/PageTransition'
import FeedbackWidget from '@/components/feedback/FeedbackWidget'
import { slideInFromRight, fadeIn } from '@/utils/animations'

export default function FraudDetectionPage() {
    const [formData, setFormData] = useState({
        customer_id: '',
        transaction_amount: '',
        kyc_verified: '1',
        account_age_days: '',
        channel: 'Web',
        timestamp: new Date().toISOString().slice(0, 16)
    })

    const [prediction, setPrediction] = useState<any>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        setPrediction(null)

        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 30000)

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
            const response = await fetch(`${apiUrl}/api/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...formData,
                    transaction_amount: parseFloat(formData.transaction_amount),
                    kyc_verified: parseInt(formData.kyc_verified),
                    account_age_days: parseInt(formData.account_age_days) || 0
                }),
                signal: controller.signal
            })

            clearTimeout(timeoutId)
            const data = await response.json()

            if (data.success) {
                setPrediction(data)
            } else {
                setError(data.error || 'Prediction failed')
            }
        } catch (err: any) {
            clearTimeout(timeoutId)
            if (err.name === 'AbortError') {
                setError('Request timeout. Please try again.')
            } else {
                setError('Failed to connect to API')
            }
        } finally {
            setLoading(false)
        }
    }

    const resetForm = () => {
        setFormData({
            customer_id: '',
            transaction_amount: '',
            kyc_verified: '1',
            account_age_days: '',
            channel: 'Web',
            timestamp: new Date().toISOString().slice(0, 16)
        })
        setPrediction(null)
        setError('')
    }

    // Calculate risk score percentage
    const riskScore = prediction?.risk_score
        ? Math.round(prediction.risk_score * 100)
        : 0


    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Shield className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-foreground">
                            Fraud Detection Lab
                        </h1>
                        <p className="text-muted-foreground">
                            Real-time transaction evaluation with AI-powered analysis
                        </p>
                    </div>
                </div>
            </motion.div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Panel */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass rounded-xl border border-border p-6"
                >
                    <h2 className="text-xl font-semibold text-foreground mb-6">
                        Transaction Details
                    </h2>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* Customer ID */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                <User className="w-4 h-4 inline mr-2" />
                                Customer ID
                            </label>
                            <input
                                type="text"
                                value={formData.customer_id}
                                onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-foreground"
                                placeholder="e.g., C12345"
                                required
                            />
                        </div>

                        {/* Transaction Amount */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                <DollarSign className="w-4 h-4 inline mr-2" />
                                Amount
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                value={formData.transaction_amount}
                                onChange={(e) => setFormData({ ...formData, transaction_amount: e.target.value })}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-foreground"
                                placeholder="e.g., 1500.00"
                                required
                            />
                        </div>

                        {/* Channel */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                <XCircle className="w-4 h-4 inline mr-2" />
                                Channel
                            </label>
                            <select
                                value={formData.channel}
                                onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-foreground cursor-pointer"
                            >
                                <option value="Web">Web</option>
                                <option value="Mobile">Mobile</option>
                                <option value="ATM">ATM</option>
                                <option value="POS">POS</option>
                                <option value="International">International</option>
                            </select>
                        </div>

                        {/* KYC Verified */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                KYC Status
                            </label>
                            <div className="flex gap-4">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        value="1"
                                        checked={formData.kyc_verified === '1'}
                                        onChange={(e) => setFormData({ ...formData, kyc_verified: e.target.value })}
                                        className="w-4 h-4 text-primary focus:ring-primary"
                                    />
                                    <span className="text-sm">Verified</span>
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        value="0"
                                        checked={formData.kyc_verified === '0'}
                                        onChange={(e) => setFormData({ ...formData, kyc_verified: e.target.value })}
                                        className="w-4 h-4 text-primary focus:ring-primary"
                                    />
                                    <span className="text-sm">Not Verified</span>
                                </label>
                            </div>
                        </div>

                        {/* Account Age */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                <Clock className="w-4 h-4 inline mr-2" />
                                Account Age (days)
                            </label>
                            <input
                                type="number"
                                value={formData.account_age_days}
                                onChange={(e) => setFormData({ ...formData, account_age_days: e.target.value })}
                                className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all text-foreground"
                                placeholder="e.g., 180"
                            />
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-3 pt-4">
                            <motion.button
                                whileHover={{ scale: 1.02, boxShadow: "0 0 20px rgba(23, 184, 151, 0.4)" }}
                                whileTap={{ scale: 0.98 }}
                                type="submit"
                                disabled={loading}
                                className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground rounded-lg font-semibold hover:from-primary/90 hover:to-primary/70 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-primary/20"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <Shield className="w-5 h-5" />
                                        Analyze Transaction
                                    </>
                                )}
                            </motion.button>
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                type="button"
                                onClick={resetForm}
                                className="px-6 py-3 bg-card hover:bg-card-hover border border-border rounded-lg font-medium transition-colors"
                            >
                                Reset
                            </motion.button>
                        </div>
                    </form>
                </motion.div>

                {/* Result Panel */}
                <div className="lg:sticky lg:top-8 h-fit">
                    <AnimatePresence mode="wait">
                        {error ? (
                            <motion.div
                                key="error"
                                variants={slideInFromRight}
                                initial="initial"
                                animate="animate"
                                exit="exit"
                                className="glass rounded-xl border border-danger/20 p-8 text-center"
                            >
                                <AlertTriangle className="w-16 h-16 text-danger mx-auto mb-4" />
                                <h3 className="text-xl font-semibold text-foreground mb-2">Error</h3>
                                <p className="text-muted-foreground">{error}</p>
                            </motion.div>
                        ) : prediction ? (
                            <motion.div
                                key="result"
                                variants={slideInFromRight}
                                initial="initial"
                                animate="animate"
                                exit="exit"
                                className="glass rounded-xl border border-border p-8 space-y-6"
                            >
                                {/* Risk Meter */}
                                <div className="flex justify-center">
                                    <RiskMeter score={riskScore} delay={0.2} />
                                </div>

                                {/* Prediction Badge */}
                                <div className="text-center">
                                    <StatusBadge
                                        status={prediction.prediction === 'Fraud' ? 'FRAUD' : 'LEGITIMATE'}
                                        severity={prediction.prediction === 'Fraud' ? 'CRITICAL' : 'LOW'}
                                        animate={prediction.prediction === 'Fraud'}
                                        size="lg"
                                    />
                                    <p className="text-sm text-muted-foreground mt-2">
                                        {prediction.prediction === 'Fraud' ? 'Transaction flagged as fraudulent' : 'Transaction appears legitimate'}
                                    </p>
                                </div>

                                {/* Triggered Rules */}
                                {prediction.details?.triggered_rules && prediction.details.triggered_rules.length > 0 && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: 0.5 }}
                                        className="p-4 bg-danger/5 border border-danger/20 rounded-lg"
                                    >
                                        <h4 className="text-sm font-semibold text-foreground mb-2">
                                            Triggered Rules ({prediction.details.triggered_rules.length})
                                        </h4>
                                        <ul className="space-y-1">
                                            {prediction.details.triggered_rules.map((rule: string, idx: number) => (
                                                <li key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
                                                    <span className="text-danger mt-0.5">•</span>
                                                    <span>{rule}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </motion.div>
                                )}

                                {/* LLM Explanation */}
                                {prediction.explanation && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: 0.7 }}
                                        className="p-4 bg-card border border-border rounded-lg"
                                    >
                                        <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                                            <span className="text-primary">✨</span>
                                            AI Explanation
                                        </h4>
                                        <p className="text-sm text-muted-foreground leading-relaxed">
                                            {prediction.explanation}
                                        </p>
                                    </motion.div>
                                )}

                                {/* Alert ID */}
                                {prediction.alert_id && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.9 }}
                                        className="text-center text-xs text-muted-foreground"
                                    >
                                        Alert ID: {prediction.alert_id}
                                    </motion.div>
                                )}

                                {/* Feedback Collection Widget */}
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 1.0 }}
                                    className="mt-6 p-6 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-xl border border-blue-500/10"
                                >
                                    <FeedbackWidget
                                        transactionId={prediction.transaction_id}
                                        prediction={prediction.prediction}
                                        onFeedbackSubmitted={() => {
                                            console.log('Feedback submitted - continuous learning active');
                                        }}
                                    />
                                </motion.div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="empty"
                                variants={fadeIn}
                                initial="initial"
                                animate="animate"
                                exit="exit"
                                className="glass rounded-xl border border-border p-12 text-center"
                            >
                                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                                    <Shield className="w-8 h-8 text-primary" />
                                </div>
                                <h3 className="text-lg font-semibold text-foreground mb-2">
                                    Ready to Analyze
                                </h3>
                                <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                                    Fill in the transaction details and click "Analyze Transaction" to get real-time fraud detection results
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    )
}
