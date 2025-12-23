'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Transaction {
    transaction_id: string;
    customer_id: string;
    kyc_verified: number;
    account_age_days: number;
    transaction_amount: number;
    channel: string;
    timestamp: string;
    is_fraud: number;
    is_high_value: number;
    account_age_bucket: string;
}

interface PaginationInfo {
    limit: number;
    offset: number;
    total: number;
    returned: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function TransactionsPage() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [pagination, setPagination] = useState<PaginationInfo | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const limit = 50;

    useEffect(() => {
        fetchTransactions();
    }, [currentPage]);

    const fetchTransactions = async () => {
        try {
            setLoading(true);
            const offset = (currentPage - 1) * limit;
            const response = await fetch(`${API_BASE_URL}/api/transactions?limit=${limit}&offset=${offset}`);
            const data = await response.json();

            if (data.success) {
                setTransactions(data.data);
                setPagination(data.pagination);
                setError(null);
            } else {
                setError('Failed to load transactions');
            }
        } catch (err) {
            setError('Error connecting to API');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const totalPages = pagination ? Math.ceil(pagination.total / limit) : 0;

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Transaction History</h1>
                            <p className="text-sm text-gray-500 mt-1">View and analyze all transactions</p>
                        </div>
                        <nav className="flex gap-4">
                            <Link href="/" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
                                Dashboard
                            </Link>
                            <Link href="/transactions" className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">
                                Transactions
                            </Link>
                            <Link href="/analytics" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
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
                {loading ? (
                    <div className="bg-white rounded-xl shadow-md p-12 text-center">
                        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                        <p className="mt-4 text-gray-600">Loading transactions...</p>
                    </div>
                ) : error ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                        <p className="text-red-600">{error}</p>
                        <button
                            onClick={fetchTransactions}
                            className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                        >
                            Retry
                        </button>
                    </div>
                ) : (
                    <>
                        {/* Stats Bar */}
                        {pagination && (
                            <div className="bg-white rounded-xl shadow-md p-4 mb-6 flex justify-between items-center">
                                <div className="text-sm text-gray-600">
                                    Showing <span className="font-semibold text-gray-900">{pagination.offset + 1}</span> to{' '}
                                    <span className="font-semibold text-gray-900">{Math.min(pagination.offset + pagination.returned, pagination.total)}</span> of{' '}
                                    <span className="font-semibold text-gray-900">{pagination.total}</span> transactions
                                </div>
                                <div className="text-sm text-gray-600">
                                    Page <span className="font-semibold text-gray-900">{currentPage}</span> of{' '}
                                    <span className="font-semibold text-gray-900">{totalPages}</span>
                                </div>
                            </div>
                        )}

                        {/* Table */}
                        <div className="bg-white rounded-xl shadow-md overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Transaction ID
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Customer
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Amount
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Channel
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                KYC
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Account Age
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Status
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {transactions.map((txn) => (
                                            <tr key={txn.transaction_id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                    {txn.transaction_id}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                                    {txn.customer_id}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    <span className={txn.is_high_value === 1 ? 'font-bold text-orange-600' : ''}>
                                                        ${txn.transaction_amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                                                        {txn.channel}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                                                    {txn.kyc_verified === 1 ? (
                                                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                                                            ✓ Verified
                                                        </span>
                                                    ) : (
                                                        <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
                                                            Not Verified
                                                        </span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 capitalize">
                                                    {txn.account_age_bucket}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                    {txn.is_fraud === 1 ? (
                                                        <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-bold">
                                                            ⚠ FRAUD
                                                        </span>
                                                    ) : (
                                                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                                                            ✓ Legitimate
                                                        </span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Pagination */}
                        {pagination && totalPages > 1 && (
                            <div className="mt-6 flex justify-center gap-2">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                                >
                                    Previous
                                </button>

                                <div className="flex gap-1">
                                    {[...Array(Math.min(5, totalPages))].map((_, i) => {
                                        const pageNum = i + 1;
                                        return (
                                            <button
                                                key={pageNum}
                                                onClick={() => setCurrentPage(pageNum)}
                                                className={`px-4 py-2 rounded-lg font-medium ${currentPage === pageNum
                                                        ? 'bg-blue-600 text-white'
                                                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                                                    }`}
                                            >
                                                {pageNum}
                                            </button>
                                        );
                                    })}
                                </div>

                                <button
                                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                                >
                                    Next
                                </button>
                            </div>
                        )}
                    </>
                )}
            </main>
        </div>
    );
}
