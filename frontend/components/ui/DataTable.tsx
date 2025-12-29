'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'

interface Column<T> {
    key: string
    label: string
    sortable?: boolean
    render?: (item: T) => React.ReactNode
    className?: string
}

interface DataTableProps<T> {
    data: T[]
    columns: Column<T>[]
    keyExtractor: (item: T) => string | number
    onRowClick?: (item: T) => void
    loading?: boolean
    emptyMessage?: string
}

export default function DataTable<T>({
    data,
    columns,
    keyExtractor,
    onRowClick,
    loading = false,
    emptyMessage = 'No data available'
}: DataTableProps<T>) {
    const [sortKey, setSortKey] = useState<string | null>(null)
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

    const handleSort = (key: string) => {
        if (sortKey === key) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
        } else {
            setSortKey(key)
            setSortOrder('asc')
        }
    }

    const sortedData = [...data].sort((a, b) => {
        if (!sortKey) return 0

        const aValue = (a as any)[sortKey]
        const bValue = (b as any)[sortKey]

        if (aValue === bValue) return 0

        const comparison = aValue > bValue ? 1 : -1
        return sortOrder === 'asc' ? comparison : -comparison
    })

    if (loading) {
        return (
            <div className="glass rounded-xl border border-border overflow-hidden">
                <div className="p-12 text-center">
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto"
                    />
                    <p className="text-muted-foreground mt-4">Loading data...</p>
                </div>
            </div>
        )
    }

    if (data.length === 0) {
        return (
            <div className="glass rounded-xl border border-border overflow-hidden">
                <div className="p-12 text-center">
                    <p className="text-muted-foreground">{emptyMessage}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="glass rounded-xl border border-border overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    {/* Header */}
                    <thead className="border-b border-border bg-muted/5 sticky top-0 z-10">
                        <tr>
                            {columns.map((column) => (
                                <th
                                    key={column.key}
                                    className={`px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider ${column.sortable ? 'cursor-pointer select-none hover:text-foreground transition-colors' : ''
                                        } ${column.className || ''}`}
                                    onClick={() => column.sortable && handleSort(column.key)}
                                >
                                    <div className="flex items-center gap-2">
                                        <span>{column.label}</span>
                                        {column.sortable && (
                                            <span className="inline-flex">
                                                {sortKey === column.key ? (
                                                    sortOrder === 'asc' ? (
                                                        <ChevronUp className="w-4 h-4" />
                                                    ) : (
                                                        <ChevronDown className="w-4 h-4" />
                                                    )
                                                ) : (
                                                    <ChevronsUpDown className="w-4 h-4 opacity-40" />
                                                )}
                                            </span>
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>

                    {/* Body */}
                    <tbody className="divide-y divide-border">
                        <AnimatePresence mode="popLayout">
                            {sortedData.map((item, index) => (
                                <motion.tr
                                    key={keyExtractor(item)}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    transition={{ delay: index * 0.02 }}
                                    whileHover={{ backgroundColor: 'hsl(var(--card-hover))' }}
                                    onClick={() => onRowClick?.(item)}
                                    className={`transition-colors ${onRowClick ? 'cursor-pointer' : ''}`}
                                >
                                    {columns.map((column) => (
                                        <td
                                            key={column.key}
                                            className={`px-6 py-4 whitespace-nowrap ${column.className || ''}`}
                                        >
                                            {column.render
                                                ? column.render(item)
                                                : String((item as any)[column.key] ?? '')}
                                        </td>
                                    ))}
                                </motion.tr>
                            ))}
                        </AnimatePresence>
                    </tbody>
                </table>
            </div>
        </div>
    )
}
