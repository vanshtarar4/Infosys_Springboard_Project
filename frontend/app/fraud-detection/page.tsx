'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function FraudDetectionPage() {
    const [formData, setFormData] = useState({
        customer_id: '',
        transaction_amount: '',
        kyc_verified: '1',
        account_age_days: '',
        channel: 'Web',
        timestamp: new Date().toISOString().slice(0, 16)
    });

    const [prediction, setPrediction] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setPrediction(null);

        try {
            const response = await fetch('http://localhost:8001/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...formData,
                    transaction_amount: parseFloat(formData.transaction_amount),
                    kyc_verified: parseInt(formData.kyc_verified),
                    account_age_days: parseInt(formData.account_age_days) || 0
                })
            });

            const data = await response.json();

            if (data.success) {
                setPrediction(data);
            } else {
                setError(data.error || 'Prediction failed');
            }
        } catch (err) {
            setError('Failed to connect to API. Make sure backend is running on port 8001.');
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setFormData({
            customer_id: '',
            transaction_amount: '',
            kyc_verified: '1',
            account_age_days: '',
            channel: 'Web',
            timestamp: new Date().toISOString().slice(0, 16)
        });
        setPrediction(null);
        setError('');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/" className="text-emerald-400 hover:text-emerald-300 mb-4 inline-flex items-center gap-2">
                        <span>←</span> Back to Dashboard
                    </Link>
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-400 mt-4">
                        Fraud Detection Lab
                    </h1>
                    <p className="text-slate-400 mt-2">Submit a transaction to evaluate fraud risk using hybrid ML + Rules engine</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Form */}
                    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 shadow-2xl">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-semibold text-emerald-400">Fraud Detection Simulator</h2>
                            <div className="w-10 h-10 bg-emerald-500/20 rounded-full flex items-center justify-center">
                                <span className="text-2xl">🛡️</span>
                            </div>
                        </div>
                        <p className="text-sm text-slate-400 mb-6">Submit a single transaction payload to evaluate its fraud risk using the hybrid ML + rules engine.</p>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Customer ID</label>
                                <input
                                    type="text"
                                    value={formData.customer_id}
                                    onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
                                    placeholder="e.g., C12345"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Transaction Amount ($)</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.transaction_amount}
                                    onChange={(e) => setFormData({ ...formData, transaction_amount: e.target.value })}
                                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
                                    placeholder="e.g., 5000"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">KYC Verified</label>
                                <select
                                    value={formData.kyc_verified}
                                    onChange={(e) => setFormData({ ...formData, kyc_verified: e.target.value })}
                                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
                                >
                                    <option value="1">Yes (1)</option>
                                    <option value="0">No (0)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Account Age (days)</label>
                                <input
                                    type="number"
                                    value={formData.account_age_days}
                                    onChange={(e) => setFormData({ ...formData, account_age_days: e.target.value })}
                                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
                                    placeholder="e.g., 100"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Channel</label>
                                <select
                                    value={formData.channel}
                                    onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
                                >
                                    <option value="Web">Web</option>
                                    <option value="Mobile">Mobile</option>
                                    <option value="POS">POS</option>
                                    <option value="ATM">ATM</option>
                                    <option value="International">International</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Timestamp</label>
                                <input
                                    type="datetime-local"
                                    value={formData.timestamp}
                                    onChange={(e) => setFormData({ ...formData, timestamp: e.target.value })}
                                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
                                />
                            </div>

                            <div className="flex gap-3 pt-2">
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20"
                                >
                                    {loading ? 'Analyzing...' : '🔍 Run Prediction'}
                                </button>
                                <button
                                    type="button"
                                    onClick={resetForm}
                                    className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg transition"
                                >
                                    Reset
                                </button>
                            </div>
                        </form>

                        {error && (
                            <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200 text-sm">
                                ⚠️ {error}
                            </div>
                        )}
                    </div>

                    {/* Results */}
                    <div className="space-y-6">
                        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 shadow-2xl">
                            <h2 className="text-2xl font-semibold text-emerald-400 mb-6">Prediction Result</h2>

                            {loading && (
                                <div className="flex items-center justify-center h-64">
                                    <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-emerald-500"></div>
                                </div>
                            )}

                            {prediction && !loading && (
                                <div className="space-y-4 animate-fadeIn">
                                    {/* Classification */}
                                    <div className={`p-6 rounded-xl border-2 ${prediction.prediction === 'Fraud'
                                            ? 'bg-red-900/30 border-red-500'
                                            : 'bg-green-900/30 border-green-500'
                                        }`}>
                                        <div className="text-center">
                                            <div className="text-6xl mb-4">
                                                {prediction.prediction === 'Fraud' ? '⚠️' : '✅'}
                                            </div>
                                            <h3 className="text-3xl font-bold mb-2">
                                                {prediction.prediction}
                                            </h3>
                                            <p className="text-slate-300 text-sm">
                                                Transaction ID: {prediction.transaction_id}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Risk Score */}
                                    <div className="bg-slate-900/50 rounded-xl p-6">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="font-medium">Final Risk Score</span>
                                            <span className="text-2xl font-bold text-emerald-400">
                                                {(prediction.risk_score * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="w-full bg-slate-700 rounded-full h-4 overflow-hidden">
                                            <div
                                                className={`h-full transition-all duration-1000 ${prediction.risk_score >= 0.7 ? 'bg-red-500' :
                                                        prediction.risk_score >= 0.4 ? 'bg-yellow-500' :
                                                            'bg-green-500'
                                                    }`}
                                                style={{ width: `${prediction.risk_score * 100}%` }}
                                            />
                                        </div>
                                        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <span className="text-slate-400">ML Score:</span>
                                                <span className="ml-2 text-white font-semibold">{(prediction.details.ml_risk_score * 100).toFixed(1)}%</span>
                                            </div>
                                            <div>
                                                <span className="text-slate-400">Rule Score:</span>
                                                <span className="ml-2 text-white font-semibold">{(prediction.details.rule_risk_score * 100).toFixed(1)}%</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Explanation */}
                                    <div className="bg-blue-900/20 border border-blue-700 rounded-xl p-6">
                                        <h4 className="font-semibold text-lg mb-3 text-blue-300 flex items-center gap-2">
                                            <span>💡</span> Risk Explanation
                                        </h4>
                                        <p className="text-slate-200 leading-relaxed">
                                            {prediction.reason}
                                        </p>
                                    </div>

                                    {/* Triggered Rules */}
                                    {prediction.details.triggered_rules.length > 0 && (
                                        <div className="bg-orange-900/20 border border-orange-700 rounded-xl p-6">
                                            <h4 className="font-semibold text-lg mb-3 text-orange-300">
                                                Triggered Rules ({prediction.details.rules_count})
                                            </h4>
                                            <ul className="space-y-2">
                                                {prediction.details.triggered_rules.map((rule: string, idx: number) => (
                                                    <li key={idx} className="flex items-start gap-2 text-sm">
                                                        <span className="text-orange-400 mt-0.5">●</span>
                                                        <span className="text-slate-200">{rule}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Alert Info */}
                                    {prediction.details.alert_id && (
                                        <div className="bg-slate-900/50 rounded-xl p-4 text-sm">
                                            <span className="text-slate-400">Alert ID:</span>
                                            <span className="ml-2 text-emerald-400 font-mono">#{prediction.details.alert_id}</span>
                                            <span className="ml-4 text-slate-500">● Saved to fraud_alerts table</span>
                                        </div>
                                    )}
                                </div>
                            )}

                            {!prediction && !loading && (
                                <div className="flex items-center justify-center h-64 text-slate-500">
                                    <div className="text-center">
                                        <div className="text-6xl mb-4">📊</div>
                                        <p>Submit a transaction to see prediction</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
