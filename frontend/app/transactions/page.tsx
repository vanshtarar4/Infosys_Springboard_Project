'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
    CreditCard,
    ArrowLeft,
    Search,
    DollarSign,
    User,
    CheckCircle,
    XCircle,
} from 'lucide-react'
import DataTable from '@/components/ui/DataTable'
import StatusBadge from '@/components/ui/StatusBadge'
import { formatCurrency, formatRelativeTime } from '@/utils/helpers'

interface Transaction {
    transaction_id: string
    user_id?: string  // API uses user_id
    customer_id?: string  // Fallback for backwards compatibility
    kyc_verified: number
    account_age_days?: number
    transaction_amount: number
    channel?: string  // Made optional since it might not always exist
    timestamp: string
    is_fraud: number
    is_high_value: number
    account_age_bucket?: string  // Made optional
}

interface PaginationInfo {
    limit: number
    offset: number
    total: number
    returned: number
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export default function TransactionsPage() {
    const [transactions, setTransactions] = useState<Transaction[]>([])
    const [pagination, setPagination] = useState<PaginationInfo | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [currentPage, setCurrentPage] = useState(1)
    const [searchTerm, setSearchTerm] = useState('')
    const limit = 25 // Reduced from 50 for better performance

    useEffect(() => {
        fetchTransactions()
    }, [currentPage])

    const fetchTransactions = async () => {
        try {
            setLoading(true)
            const offset = (currentPage - 1) * limit
            const response = await fetch(`${API_BASE_URL}/api/transactions?limit=${limit}&offset=${offset}`)
            const data = await response.json()

            if (data.success) {
                setTransactions(data.data)
                setPagination(data.pagination)
                setError(null)
            } else {
                setError('Failed to load transactions')
            }
        } catch (err) {
            setError('Error connecting to API')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const totalPages = pagination ? Math.ceil(pagination.total / limit) : 0

    // Filter transactions based on search
    const filteredTransactions = transactions.filter(txn =>
        txn.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        txn.user_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        txn.customer_id?.toLowerCase().includes(searchTerm.toLowerCase())
    )

    const columns = [
        {
            key: 'transaction_id',
            label: 'Transaction',
            sortable: true,
            render: (txn: Transaction) => (
                <div>
                    <div className="text-sm font-medium text-foreground">{txn.transaction_id}</div>
                    <div className="text-xs text-muted-foreground">{formatRelativeTime(txn.timestamp)}</div>
                </div>
            )
        },
        {
            key: 'customer_id',
            label: 'Customer',
            sortable: true,
            render: (txn: Transaction) => (
                <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-foreground">{txn.user_id || txn.customer_id || 'N/A'}</span>
                </div>
            )
        },
        {
            key: 'transaction_amount',
            label: 'Amount',
            sortable: true,
            render: (txn: Transaction) => (
                <div className={`text-sm font-semibold ${txn.is_high_value ? 'text-warning' : 'text-foreground'}`}>
                    {formatCurrency(txn.transaction_amount)}
                    {txn.is_high_value === 1 && (
                        <span className="ml-2 text-xs text-warning">HIGH VALUE</span>
                    )}
                </div>
            )
        },
        {
            key: 'channel',
            label: 'Channel',
            sortable: true,
            render: (txn: Transaction) => (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary/10 text-secondary border border-secondary/20">
                    {txn.channel || 'N/A'}
                </span>
            )
        },
        {
            key: 'kyc_verified',
            label: 'KYC',
            sortable: true,
            render: (txn: Transaction) =>
                txn.kyc_verified === 1 ? (
                    <div className="flex items-center gap-1.5 text-success text-sm">
                        <CheckCircle className="w-4 h-4" />
                        <span>Verified</span>
                    </div>
                ) : (
                    <div className="flex items-center gap-1.5 text-warning text-sm">
                        <XCircle className="w-4 h-4" />
                        <span>Pending</span>
                    </div>
                )
        },
        {
            key: 'account_age_bucket',
            label: 'Account Age',
            sortable: true,
            render: (txn: Transaction) => (
                <span className="text-sm text-muted-foreground capitalize">
                    {txn.account_age_bucket || (txn.account_age_days ? `${txn.account_age_days}d` : 'N/A')}
                </span>
            )
        },
        {
            key: 'is_fraud',
            label: 'Status',
            sortable: true,
            render: (txn: Transaction) => (
                <StatusBadge
                    status={txn.is_fraud === 1 ? 'FRAUD' : 'LEGITIMATE'}
                    severity={txn.is_fraud === 1 ? 'CRITICAL' : 'LOW'}
                    animate={txn.is_fraud === 1}
                    size="sm"
                />
            )
        },
    ]

    return (
        <div className="space-y-6">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >

                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                            <CreditCard className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-foreground">
                                Transaction History
                            </h1>
                            <p className="text-muted-foreground">
                                View and analyze all transactions
                            </p>
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Stats & Search */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Stats */}
                {pagination && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass rounded-xl border border-border p-4"
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Transactions</p>
                                <p className="text-2xl font-bold text-foreground">{pagination.total.toLocaleString()}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-sm text-muted-foreground">Showing</p>
                                <p className="text-sm font-medium text-foreground">
                                    {pagination.offset + 1} - {Math.min(pagination.offset + pagination.returned, pagination.total)}
                                </p>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Search */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass rounded-xl border border-border p-4"
                >
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Search by Transaction ID or Customer..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none text-foreground placeholder:text-muted-foreground"
                        />
                    </div>
                </motion.div>
            </div>

            {/* Table */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
            >
                <DataTable
                    data={filteredTransactions}
                    columns={columns}
                    keyExtractor={(txn) => txn.transaction_id}
                    loading={loading}
                    emptyMessage={searchTerm ? 'No transactions match your search' : 'No transactions found'}
                />
            </motion.div>

            {/* Pagination */}
            {pagination && totalPages > 1 && !searchTerm && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="flex justify-center gap-2"
                >
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                        className="px-4 py-2 glass border border-border rounded-lg text-foreground hover:bg-card-hover disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
                    >
                        Previous
                    </motion.button>

                    <div className="flex items-center gap-2 px-4 py-2 glass border border-border rounded-lg">
                        <span className="text-sm text-muted-foreground">Page</span>
                        <span className="text-sm font-semibold text-foreground">{currentPage}</span>
                        <span className="text-sm text-muted-foreground">of</span>
                        <span className="text-sm font-semibold text-foreground">{totalPages}</span>
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                        className="px-4 py-2 glass border border-border rounded-lg text-foreground hover:bg-card-hover disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
                    >
                        Next
                    </motion.button>
                </motion.div>
            )}
        </div>
    )
}
