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
            setError('Failed to connect to API');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/" className="text-teal-400 hover:text-teal-300 mb-4 inline-block">
                        ← Back to Dashboard
                    </Link>
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-emerald-400">
                        Fraud Detection Lab
                    </h1>
                    <p className="text-slate-400 mt-2">Submit a transaction to evaluate fraud risk using ML</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Form */}
                    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                        <h2 className="text-2xl font-semibold mb-6 text-teal-400">Transaction Details</h2>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Customer ID</label>
                                <input
                                    type="text"
                                    value={formData.customer_id}
                                    onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                                    className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
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
                                    className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
                                    placeholder="e.g., 5000"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">KYC Verified</label>
                                <select
                                    value={formData.kyc_verified}
                                    onChange={(e) => setFormData({ ...formData, kyc_verified: e.target.value })}
                                    className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
                                >
                                    <option value="1">Yes</option>
                                    <option value="0">No</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Account Age (days)</label>
                                <input
                                    type="number"
                                    value={formData.account_age_days}
                                    onChange={(e) => setFormData({ ...formData, account_age_days: e.target.value })}
                                    className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
                                    placeholder="e.g., 100"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Channel</label>
                                <select
                                    value={formData.channel}
                                    onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                                    className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
                                >
                                    <option value="Web">Web</option>
                                    <option value="Mobile">Mobile</option>
                                    <option value="POS">POS</option>
                                    <option value="ATM">ATM</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Analyzing...' : '🔍 Run Prediction'}
                            </button>
                        </form>

                        {error && (
                            <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
                                {error}
                            </div>
                        )}
                    </div>

                    {/* Results */}
                    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
                        <h2 className="text-2xl font-semibold mb-6 text-teal-400">Prediction Result</h2>

                        {loading && (
                            <div className="flex items-center justify-center h-64">
                                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-teal-500"></div>
                            </div>
                        )}

                        {prediction && !loading && (
                            <div className="space-y-6 animate-fadeIn">
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
                                        <p className="text-slate-300">
                                            Classification Result
                                        </p>
                                    </div>
                                </div>

                                {/* Risk Score */}
                                <div className="bg-slate-900/50 rounded-xl p-6">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium">Risk Score</span>
                                        <span className="text-2xl font-bold text-teal-400">
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
                                    <p className="text-sm text-slate-400 mt-2">
                                        Threshold: {(prediction.threshold * 100).toFixed(0)}%
                                    </p>
                                </div>

                                {/* Details */}
                                <div className="bg-slate-900/50 rounded-xl p-6 space-y-3">
                                    <h4 className="font-semibold text-lg mb-4">Analysis Details</h4>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Customer ID</span>
                                        <span className="font-mono">{prediction.customer_id}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Confidence</span>
                                        <span>{(prediction.confidence * 100).toFixed(1)}%</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Model Threshold</span>
                                        <span>{prediction.threshold}</span>
                                    </div>
                                </div>
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
    );
}
