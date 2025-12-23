'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function ModelPerformancePage() {
    const [metrics, setMetrics] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchMetrics();
    }, []);

    const fetchMetrics = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/model/metrics');
            const data = await response.json();

            if (data.success) {
                setMetrics(data.metrics);
            } else {
                setError(data.error);
            }
        } catch (err) {
            setError('Failed to load metrics');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-teal-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-red-900/50 border border-red-700 rounded-xl p-6 text-red-200">
                        {error}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/" className="text-teal-400 hover:text-teal-300 mb-4 inline-block">
                        ← Back to Dashboard
                    </Link>
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-emerald-400">
                        Model Performance
                    </h1>
                    <p className="text-slate-400 mt-2">
                        {metrics?.model_name || 'Fraud Detection Model'} • Threshold: {metrics?.threshold || 0.5}
                    </p>
                </div>

                {/* Core Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
                    <MetricCard
                        title="Accuracy"
                        value={metrics?.accuracy}
                        icon="🎯"
                        color="blue"
                    />
                    <MetricCard
                        title="Precision"
                        value={metrics?.precision}
                        icon="📊"
                        color="purple"
                    />
                    <MetricCard
                        title="Recall"
                        value={metrics?.recall}
                        icon="⭐"
                        color="emerald"
                        highlight={true}
                    />
                    <MetricCard
                        title="F1-Score"
                        value={metrics?.f1_score}
                        icon="📈"
                        color="orange"
                    />
                    <MetricCard
                        title="ROC-AUC"
                        value={metrics?.roc_auc}
                        icon="📉"
                        color="teal"
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    {/* Fraud Detection Stats */}
                    {metrics?.fraud_detection && (
                        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                            <h2 className="text-2xl font-semibold mb-6 text-teal-400">Fraud Detection Performance</h2>

                            <div className="space-y-4">
                                <div className="flex justify-between items-center p-4 bg-slate-900/50 rounded-lg">
                                    <span className="text-slate-300">Detection Rate</span>
                                    <span className="text-2xl font-bold text-emerald-400">
                                        {(metrics.fraud_detection.detection_rate * 100).toFixed(1)}%
                                    </span>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="p-4 bg-green-900/30 border border-green-700 rounded-lg">
                                        <div className="text-3xl font-bold text-green-400">
                                            {metrics.fraud_detection.frauds_detected}
                                        </div>
                                        <div className="text-sm text-slate-400 mt-1">Frauds Detected</div>
                                    </div>

                                    <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg">
                                        <div className="text-3xl font-bold text-red-400">
                                            {metrics.fraud_detection.frauds_missed}
                                        </div>
                                        <div className="text-sm text-slate-400 mt-1">Frauds Missed</div>
                                    </div>
                                </div>

                                <div className="p-4 bg-slate-900/50 rounded-lg">
                                    <div className="text-sm text-slate-400 mb-2">Total Fraud Cases</div>
                                    <div className="text-xl font-semibold">
                                        {metrics.fraud_detection.total_fraud_cases}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Confusion Matrix */}
                    {metrics?.confusion_matrix && (
                        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                            <h2 className="text-2xl font-semibold mb-6 text-teal-400">Confusion Matrix</h2>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-6 bg-green-900/30 border-2 border-green-700 rounded-xl">
                                    <div className="text-4xl font-bold text-green-400">
                                        {metrics.confusion_matrix.true_negatives}
                                    </div>
                                    <div className="text-sm text-slate-300 mt-2">True Negatives</div>
                                    <div className="text-xs text-slate-500">Correctly predicted legit</div>
                                </div>

                                <div className="p-6 bg-yellow-900/30 border-2 border-yellow-700 rounded-xl">
                                    <div className="text-4xl font-bold text-yellow-400">
                                        {metrics.confusion_matrix.false_positives}
                                    </div>
                                    <div className="text-sm text-slate-300 mt-2">False Positives</div>
                                    <div className="text-xs text-slate-500">False alarms</div>
                                </div>

                                <div className="p-6 bg-red-900/30 border-2 border-red-700 rounded-xl">
                                    <div className="text-4xl font-bold text-red-400">
                                        {metrics.confusion_matrix.false_negatives}
                                    </div>
                                    <div className="text-sm text-slate-300 mt-2">False Negatives</div>
                                    <div className="text-xs text-slate-500">Missed fraud</div>
                                </div>

                                <div className="p-6 bg-emerald-900/30 border-2 border-emerald-700 rounded-xl">
                                    <div className="text-4xl font-bold text-emerald-400">
                                        {metrics.confusion_matrix.true_positives}
                                    </div>
                                    <div className="text-sm text-slate-300 mt-2">True Positives</div>
                                    <div className="text-xs text-slate-500">Correctly caught fraud</div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Metric Comparison */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                    <h2 className="text-2xl font-semibold mb-6 text-teal-400">Metrics Comparison</h2>

                    <div className="space-y-4">
                        {['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc'].map((key) => (
                            <div key={key} className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="capitalize text-slate-300">{key.replace('_', ' ')}</span>
                                    <span className="font-semibold">{(metrics[key] * 100).toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                                    <div
                                        className={`h-full transition-all duration-1000 ${key === 'recall' ? 'bg-emerald-500' : 'bg-teal-500'
                                            }`}
                                        style={{ width: `${metrics[key] * 100}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-6 p-4 bg-teal-900/30 border border-teal-700 rounded-lg">
                        <p className="text-sm text-teal-200">
                            <strong>Note:</strong> This model is optimized for <strong>recall</strong> (catching fraud)
                            over precision (minimizing false alarms), which is appropriate for fraud detection use cases.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function MetricCard({ title, value, icon, color, highlight }: any) {
    const colorClasses = {
        blue: 'border-blue-500 bg-blue-900/30',
        purple: 'border-purple-500 bg-purple-900/30',
        emerald: 'border-emerald-500 bg-emerald-900/30',
        orange: 'border-orange-500 bg-orange-900/30',
        teal: 'border-teal-500 bg-teal-900/30',
    };

    return (
        <div className={`p-6 rounded-xl border-2 ${highlight ? 'ring-2 ring-emerald-500' : ''} ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}`}>
            <div className="text-3xl mb-2">{icon}</div>
            <div className="text-3xl font-bold mb-1">
                {value ? (value * 100).toFixed(1) + '%' : 'N/A'}
            </div>
            <div className="text-sm text-slate-400">{title}</div>
            {highlight && (
                <div className="mt-2 text-xs text-emerald-400 font-semibold">
                    Primary Metric
                </div>
            )}
        </div>
    );
}
