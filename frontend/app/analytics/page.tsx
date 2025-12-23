'use client';

import Link from 'next/link';
import Image from 'next/image';

export default function AnalyticsPage() {
    const charts = [
        {
            name: 'Fraud Distribution',
            file: 'fig1_fraud_count.png',
            description: 'Count of legitimate vs fraudulent transactions'
        },
        {
            name: 'Transaction Amounts',
            file: 'fig2_box_amount.png',
            description: 'Amount distribution by fraud status'
        },
        {
            name: 'Time Patterns',
            file: 'fig3_heatmap_time.png',
            description: 'Activity heatmap by weekday and hour'
        },
        {
            name: 'Channel Risk',
            file: 'fig4_channel_fraud.png',
            description: 'Fraud rates across different channels'
        },
        {
            name: 'Account Age Risk',
            file: 'fig5_segment_risk.png',
            description: 'Risk segmentation by account age'
        },
        {
            name: 'KYC Impact',
            file: 'fig6_kyc_impact.png',
            description: 'KYC verification effectiveness'
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
                            <p className="text-sm text-gray-500 mt-1">Exploratory Data Analysis Visualizations</p>
                        </div>
                        <nav className="flex gap-4">
                            <Link href="/" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
                                Dashboard
                            </Link>
                            <Link href="/transactions" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
                                Transactions
                            </Link>
                            <Link href="/analytics" className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">
                                Analytics
                            </Link>
                            <Link href="/upload" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
                                Upload
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="bg-white rounded-xl shadow-md p-6 mb-8">
                    <h2 className="text-xl font-bold text-gray-900 mb-2">EDA Insights</h2>
                    <p className="text-gray-600">
                        Explore comprehensive visualizations from our exploratory data analysis. These charts reveal patterns in fraud detection, transaction behaviors, and risk factors.
                    </p>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {charts.map((chart) => (
                        <div key={chart.file} className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200 hover:shadow-lg transition-shadow">
                            <div className="p-6">
                                <h3 className="text-lg font-bold text-gray-900 mb-2">{chart.name}</h3>
                                <p className="text-sm text-gray-600 mb-4">{chart.description}</p>
                            </div>
                            <div className="relative w-full bg-gray-50 p-4">
                                <div className="aspect-video relative">
                                    <Image
                                        src={`/assets/charts/${chart.file}`}
                                        alt={chart.name}
                                        fill
                                        className="object-contain"
                                        unoptimized
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Note about images */}
                <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
                    <div className="flex gap-3">
                        <svg className="h-6 w-6 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                            <h3 className="text-sm font-semibold text-blue-900 mb-1">Chart Images</h3>
                            <p className="text-sm text-blue-800">
                                To display these charts, copy the PNG files from <code className="bg-blue-100 px-1 rounded">docs/figs/</code> to <code className="bg-blue-100 px-1 rounded">frontend/public/assets/charts/</code>
                            </p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
