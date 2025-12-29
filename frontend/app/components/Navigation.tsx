'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
    const pathname = usePathname();

    const navLinks = [
        { href: '/', label: 'Dashboard', icon: '📊' },
        { href: '/fraud-detection', label: 'Fraud Lab', icon: '🔍' },
        { href: '/alerts', label: 'Alerts', icon: '🚨' },
        { href: '/model-performance', label: 'Performance', icon: '📈' },
        { href: '/transactions', label: 'Transactions', icon: '💳' },
        { href: '/analytics', label: 'Analytics', icon: '📉' },
        { href: '/upload', label: 'Upload', icon: '📤' },
    ];

    return (
        <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">
                            Predictive Transaction Intelligence
                        </h1>
                        <p className="text-sm text-gray-500 mt-1">Real-Time Fraud Detection System</p>
                    </div>
                    <nav className="flex flex-wrap gap-2">
                        {navLinks.map((link) => {
                            const isActive = pathname === link.href;
                            return (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${isActive
                                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                                            : 'text-gray-700 hover:bg-gray-100'
                                        }`}
                                >
                                    <span className="mr-1">{link.icon}</span>
                                    {link.label}
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </div>
        </header>
    );
}
