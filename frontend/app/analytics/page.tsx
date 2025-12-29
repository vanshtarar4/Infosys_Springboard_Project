'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Image from 'next/image'
import {
    BarChart3,
    ArrowLeft,
    TrendingUp,
    PieChart,
    Activity,
    Info,
} from 'lucide-react'
import { staggerContainer, staggerItem } from '@/utils/animations'

export default function AnalyticsPage() {
    const charts = [
        {
            name: 'Fraud Distribution',
            file: 'fig1_fraud_count.png',
            description: 'Count of legitimate vs fraudulent transactions',
            icon: PieChart,
            color: 'primary'
        },
        {
            name: 'Transaction Amounts',
            file: 'fig2_box_amount.png',
            description: 'Amount distribution by fraud status',
            icon: BarChart3,
            color: 'success'
        },
        {
            name: 'Time Patterns',
            file: 'fig3_heatmap_time.png',
            description: 'Activity heatmap by weekday and hour',
            icon: Activity,
            color: 'warning'
        },
        {
            name: 'Channel Risk',
            file: 'fig4_channel_fraud.png',
            description: 'Fraud rates across different channels',
            icon: TrendingUp,
            color: 'danger'
        },
        {
            name: 'Account Age Risk',
            file: 'fig5_segment_risk.png',
            description: 'Risk segmentation by account age',
            icon: BarChart3,
            color: 'info'
        },
        {
            name: 'KYC Impact',
            file: 'fig6_kyc_impact.png',
            description: 'KYC verification effectiveness',
            icon: Activity,
            color: 'success'
        }
    ]

    const getColorClass = (color: string) => {
        const colors = {
            primary: 'bg-primary/10 text-primary border-primary/20',
            success: 'bg-success/10 text-success border-success/20',
            warning: 'bg-warning/10 text-warning border-warning/20',
            danger: 'bg-danger/10 text-danger border-danger/20',
            info: 'bg-secondary/10 text-secondary border-secondary/20',
        }
        return colors[color as keyof typeof colors] || colors.primary
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                        <BarChart3 className="w-6 h-6 text-secondary" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-foreground">
                            Analytics Dashboard
                        </h1>
                        <p className="text-muted-foreground">
                            Exploratory Data Analysis Visualizations
                        </p>
                    </div>
                </div>
            </motion.div>

            {/* Description Card */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="glass rounded-xl border border-border p-6"
            >
                <h2 className="text-xl font-semibold text-foreground mb-2">EDA Insights</h2>
                <p className="text-muted-foreground">
                    Explore comprehensive visualizations from our exploratory data analysis. These charts reveal patterns in fraud detection, transaction behaviors, and risk factors.
                </p>
            </motion.div>

            {/* Charts Grid */}
            <motion.div
                variants={staggerContainer}
                initial="initial"
                animate="animate"
                className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
                {charts.map((chart, index) => (
                    <motion.div
                        key={chart.file}
                        variants={staggerItem}
                        whileHover={{ scale: 1.02, y: -4 }}
                        className="glass rounded-xl border border-border overflow-hidden group"
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-border">
                            <div className="flex items-start gap-4">
                                <div className={`w-12 h-12 rounded-lg flex items-center justify-center border ${getColorClass(chart.color)}`}>
                                    <chart.icon className="w-6 h-6" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-foreground mb-1">
                                        {chart.name}
                                    </h3>
                                    <p className="text-sm text-muted-foreground">
                                        {chart.description}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Chart Image */}
                        <div className="relative w-full bg-muted/5 p-4">
                            <div className="aspect-video relative rounded-lg overflow-hidden bg-background border border-border">
                                <Image
                                    src={`/assets/charts/${chart.file}`}
                                    alt={chart.name}
                                    fill
                                    className="object-contain p-2"
                                    unoptimized
                                />
                            </div>
                        </div>
                    </motion.div>
                ))}
            </motion.div>

            {/* Info Note */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="glass rounded-xl border border-secondary/20 bg-secondary/5 p-6"
            >
                <div className="flex gap-3">
                    <Info className="w-6 h-6 text-secondary flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 className="text-sm font-semibold text-foreground mb-2">Chart Images</h3>
                        <p className="text-sm text-muted-foreground">
                            To display these charts, copy the PNG files from{' '}
                            <code className="px-2 py-0.5 rounded bg-muted text-foreground font-mono text-xs">
                                docs/figs/
                            </code>{' '}
                            to{' '}
                            <code className="px-2 py-0.5 rounded bg-muted text-foreground font-mono text-xs">
                                frontend/public/assets/charts/
                            </code>
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    )
}
