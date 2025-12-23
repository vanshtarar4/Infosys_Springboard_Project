'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Alert {
    alert_id: number;
    transaction_id: string;
    customer_id: string;
    risk_score: number;
    severity: string;
    status: string;
    alert_message: string;
    triggered_rules: string[];
    created_at: string;
    alert_type: string;
}

export default function AlertsPage() {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filter, setFilter] = useState({
        severity: '',
        status: ''
    });

    const fetchAlerts = async () => {
        try {
            const params = new URLSearchParams();
            if (filter.severity) params.append('severity', filter.severity);
            if (filter.status) params.append('status', filter.status);

            const response = await fetch(`http://localhost:8001/api/alerts?${params}`);
            const data = await response.json();

            if (data.success) {
                setAlerts(data.alerts);
                setError('');
            } else {
                setError(data.error);
            }
        } catch (err) {
            setError('Failed to fetch alerts');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAlerts();

        // Auto-refresh every 10 seconds
        const interval = setInterval(fetchAlerts, 10000);

        return () => clearInterval(interval);
    }, [filter]);

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'CRITICAL': return 'bg-red-900/50 border-red-500 text-red-200';
            case 'HIGH': return 'bg-orange-900/50 border-orange-500 text-orange-200';
            case 'MEDIUM': return 'bg-yellow-900/50 border-yellow-500 text-yellow-200';
            case 'LOW': return 'bg-blue-900/50 border-blue-500 text-blue-200';
            default: return 'bg-slate-900/50 border-slate-500 text-slate-200';
        }
    };

    const getRiskColor = (risk: number) => {
        if (risk >= 0.8) return 'text-red-400';
        if (risk >= 0.6) return 'text-orange-400';
        if (risk >= 0.4) return 'text-yellow-400';
        return 'text-green-400';
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'NEW': return 'bg-red-500';
            case 'INVESTIGATING': return 'bg-yellow-500';
            case 'RESOLVED': return 'bg-green-500';
            case 'FALSE_POSITIVE': return 'bg-blue-500';
            case 'CONFIRMED': return 'bg-purple-500';
            default: return 'bg-slate-500';
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/" className="text-emerald-400 hover:text-emerald-300 mb-4 inline-flex items-center gap-2">
                        <span>←</span> Back to Dashboard
                    </Link>
                    <div className="flex items-center justify-between mt-4">
                        <div>
                            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-400 to-orange-400">
                                Fraud Alerts Monitor
                            </h1>
                            <p className="text-slate-400 mt-2">Real-time fraud detection alerts • Auto-refresh every 10s</p>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                            <span className="text-sm text-slate-400">Live</span>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-4 mb-6">
                    <div className="flex gap-4 items-center">
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-2">Severity</label>
                            <select
                                value={filter.severity}
                                onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                                className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                            >
                                <option value="">All Severities</option>
                                <option value="CRITICAL">Critical</option>
                                <option value="HIGH">High</option>
                                <option value="MEDIUM">Medium</option>
                                <option value="LOW">Low</option>
                            </select>
                        </div>
                        <div className="flex-1">
                            <label className="block text-sm font-medium mb-2">Status</label>
                            <select
                                value={filter.status}
                                onChange={(e) => setFilter({ ...filter, status: e.target.value })}
                                className="w-full px-4 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                            >
                                <option value="">All Statuses</option>
                                <option value="NEW">New</option>
                                <option value="INVESTIGATING">Investigating</option>
                                <option value="RESOLVED">Resolved</option>
                                <option value="FALSE_POSITIVE">False Positive</option>
                                <option value="CONFIRMED">Confirmed</option>
                            </select>
                        </div>
                        <div className="pt-7">
                            <button
                                onClick={() => setFilter({ severity: '', status: '' })}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition"
                            >
                                Clear
                            </button>
                        </div>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-red-900/20 border border-red-700 rounded-xl p-4">
                        <div className="text-3xl font-bold text-red-400">
                            {alerts.filter(a => a.severity === 'CRITICAL').length}
                        </div>
                        <div className="text-sm text-slate-400 mt-1">Critical Alerts</div>
                    </div>
                    <div className="bg-orange-900/20 border border-orange-700 rounded-xl p-4">
                        <div className="text-3xl font-bold text-orange-400">
                            {alerts.filter(a => a.severity === 'HIGH').length}
                        </div>
                        <div className="text-sm text-slate-400 mt-1">High Risk</div>
                    </div>
                    <div className="bg-yellow-900/20 border border-yellow-700 rounded-xl p-4">
                        <div className="text-3xl font-bold text-yellow-400">
                            {alerts.filter(a => a.severity === 'MEDIUM').length}
                        </div>
                        <div className="text-sm text-slate-400 mt-1">Medium Risk</div>
                    </div>
                    <div className="bg-emerald-900/20 border border-emerald-700 rounded-xl p-4">
                        <div className="text-3xl font-bold text-emerald-400">
                            {alerts.filter(a => a.status === 'NEW').length}
                        </div>
                        <div className="text-sm text-slate-400 mt-1">New / Pending</div>
                    </div>
                </div>

                {/* Alerts Table */}
                <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
                    <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                        <h2 className="text-xl font-semibold">Fraud Alerts ({alerts.length})</h2>
                        <button
                            onClick={fetchAlerts}
                            className="text-emerald-400 hover:text-emerald-300 text-sm flex items-center gap-2"
                        >
                            <span>🔄</span> Refresh
                        </button>
                    </div>

                    {loading ? (
                        <div className="flex items-center justify-center py-16">
                            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
                        </div>
                    ) : error ? (
                        <div className="p-8 text-center text-red-400">
                            ⚠️ {error}
                        </div>
                    ) : alerts.length === 0 ? (
                        <div className="p-8 text-center text-slate-500">
                            <div className="text-6xl mb-4">✅</div>
                            <p>No fraud alerts found</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-slate-900/50">
                                    <tr className="text-left text-sm text-slate-400">
                                        <th className="px-6 py-3">Alert ID</th>
                                        <th className="px-6 py-3">Transaction</th>
                                        <th className="px-6 py-3">Customer</th>
                                        <th className="px-6 py-3">Risk Score</th>
                                        <th className="px-6 py-3">Severity</th>
                                        <th className="px-6 py-3">Status</th>
                                        <th className="px-6 py-3">Reason</th>
                                        <th className="px-6 py-3">Created</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-700">
                                    {alerts.map((alert) => (
                                        <tr key={alert.alert_id} className="hover:bg-slate-700/30 transition">
                                            <td className="px-6 py-4">
                                                <span className="font-mono text-sm text-emerald-400">#{alert.alert_id}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="font-mono text-sm">{alert.transaction_id}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-sm">{alert.customer_id}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <span className={`text-lg font-bold ${getRiskColor(alert.risk_score)}`}>
                                                        {(alert.risk_score * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(alert.severity)}`}>
                                                    {alert.severity}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-2">
                                                    <div className={`w-2 h-2 rounded-full ${getStatusColor(alert.status)}`}></div>
                                                    <span className="text-sm">{alert.status.replace('_', ' ')}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 max-w-md">
                                                <p className="text-sm text-slate-300 line-clamp-2">
                                                    {alert.alert_message}
                                                </p>
                                                {alert.triggered_rules && alert.triggered_rules.length > 0 && (
                                                    <div className="mt-1 flex gap-1 flex-wrap">
                                                        {alert.triggered_rules.slice(0, 2).map((rule, idx) => (
                                                            <span key={idx} className="text-xs bg-orange-900/30 text-orange-300 px-2 py-0.5 rounded">
                                                                {rule.split(' ').slice(0, 3).join(' ')}
                                                            </span>
                                                        ))}
                                                        {alert.triggered_rules.length > 2 && (
                                                            <span className="text-xs text-slate-500">+{alert.triggered_rules.length - 2} more</span>
                                                        )}
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="text-sm text-slate-400">{formatDate(alert.created_at)}</span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
