'use client'

import Sidebar from './Sidebar'
import TopBar from './TopBar'

export default function LayoutWrapper({ children }: { children: React.ReactNode }) {
    return (
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
    )
}
