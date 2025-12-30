'use client'

import { usePathname } from 'next/navigation'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import ProtectedRoute from '../auth/ProtectedRoute'

export default function LayoutWrapper({ children }: { children: React.ReactNode }) {
    const pathname = usePathname()

    // Don't show sidebar/topbar on login page
    if (pathname === '/login') {
        return <>{children}</>
    }

    return (
        <ProtectedRoute>
            <div className="flex h-screen overflow-hidden bg-background">
                {/* Sidebar */}
                <Sidebar />

                {/* Main Content Area */}
                <div className="flex-1 flex flex-col ml-[240px] transition-all duration-300">
                    {/* Top Bar */}
                    <TopBar />

                    {/* Page Content */}
                    <main className="flex-1 overflow-y-auto">
                        <div className="container mx-auto p-6 max-w-7xl">
                            {children}
                        </div>
                    </main>
                </div>
            </div>
        </ProtectedRoute>
    )
}
