'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        // Placeholder for upload functionality
        // Will be implemented when backend upload endpoint is ready
        setTimeout(() => {
            alert('Upload endpoint will be implemented in backend');
            setUploading(false);
        }, 1000);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Upload Data</h1>
                            <p className="text-sm text-gray-500 mt-1">Import new transaction files</p>
                        </div>
                        <nav className="flex gap-4">
                            <Link href="/" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
                                Dashboard
                            </Link>
                            <Link href="/transactions" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
                                Transactions
                            </Link>
                            <Link href="/analytics" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium">
                                Analytics
                            </Link>
                            <Link href="/upload" className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">
                                Upload
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="bg-white rounded-xl shadow-md p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Transaction File</h2>

                    {/* Upload Area */}
                    <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-500 transition-colors">
                        <svg className="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>

                        <div className="mt-4">
                            <label htmlFor="file-upload" className="cursor-pointer">
                                <span className="mt-2 block text-sm font-medium text-gray-900">
                                    {file ? file.name : 'Drop your CSV file here, or click to browse'}
                                </span>
                                <input
                                    id="file-upload"
                                    name="file-upload"
                                    type="file"
                                    accept=".csv"
                                    className="sr-only"
                                    onChange={handleFileChange}
                                />
                            </label>
                            <p className="mt-1 text-xs text-gray-500">CSV files up to 10MB</p>
                        </div>

                        {file && (
                            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
                                <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="text-sm text-blue-900 font-medium">{file.name}</span>
                                <button onClick={() => setFile(null)} className="ml-2 text-blue-600 hover:text-blue-800">
                                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Upload Button */}
                    <div className="mt-6 flex justify-end">
                        <button
                            onClick={handleUpload}
                            disabled={!file || uploading}
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {uploading ? (
                                <>
                                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-solid border-white border-r-transparent"></div>
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                                    </svg>
                                    Upload File
                                </>
                            )}
                        </button>
                    </div>

                    {/* Info */}
                    <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex gap-3">
                            <svg className="h-6 w-6 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <div>
                                <h3 className="text-sm font-semibold text-yellow-900 mb-1">Note</h3>
                                <p className="text-sm text-yellow-800">
                                    This is a placeholder upload component. Backend upload endpoint will be implemented to process CSV files and add them to the database.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* File Format Info */}
                    <div className="mt-6 bg-gray-50 rounded-lg p-6">
                        <h3 className="text-sm font-semibold text-gray-900 mb-3">Required CSV Format</h3>
                        <div className="text-sm text-gray-600 space-y-2">
                            <p>Your CSV file should include the following columns:</p>
                            <ul className="list-disc list-inside ml-4 space-y-1">
                                <li>transaction_id</li>
                                <li>customer_id</li>
                                <li>kyc_verified</li>
                                <li>account_age_days</li>
                                <li>transaction_amount</li>
                                <li>channel</li>
                                <li>timestamp</li>
                                <li>is_fraud</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
