"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThumbsUp, ThumbsDown, MessageSquare, CheckCircle, AlertCircle } from 'lucide-react';

interface FeedbackWidgetProps {
    transactionId: string;
    prediction: string;
    onFeedbackSubmitted?: () => void;
}

export default function FeedbackWidget({
    transactionId,
    prediction,
    onFeedbackSubmitted
}: FeedbackWidgetProps) {
    const [feedbackGiven, setFeedbackGiven] = useState(false);
    const [showNotes, setShowNotes] = useState(false);
    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);


    const submitFeedback = async (actualLabel: 'Fraud' | 'Legitimate') => {
        setLoading(true);
        setError(null);

        try {
            const requestBody = {
                transaction_id: transactionId,
                actual_label: actualLabel,
                notes: notes || '',
            };

            console.log('=== FEEDBACK SUBMISSION DEBUG ===');
            console.log('Transaction ID:', transactionId);
            console.log('Actual Label:', actualLabel);
            console.log('Request Body:', JSON.stringify(requestBody, null, 2));
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
            console.log('API URL:', `${apiUrl}/api/feedback`);

            const response = await fetch(`${apiUrl}/api/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            console.log('Response Status:', response.status, response.statusText);
            console.log('Response OK:', response.ok);
            console.log('Response Headers:', {
                'content-type': response.headers.get('content-type'),
                'content-length': response.headers.get('content-length'),
            });

            // Get response text first to see what we're dealing with
            const responseText = await response.text();
            console.log('Raw Response Text:', responseText);

            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                console.error('Non-JSON response received');
                console.error('Content-Type:', contentType);
                console.error('Response:', responseText);
                setError('Server error - non-JSON response');
                return;
            }

            // Parse JSON from text
            let data;
            try {
                data = JSON.parse(responseText);
                console.log('Parsed Response Data:', data);
            } catch (parseError) {
                console.error('JSON Parse Error:', parseError);
                console.error('Response Text:', responseText);
                setError('Invalid server response - cannot parse JSON');
                return;
            }

            if (response.ok) {
                console.log('✓ Feedback submitted successfully!');
                setFeedbackGiven(true);
                if (onFeedbackSubmitted) {
                    onFeedbackSubmitted();
                }
            } else {
                const errorMsg = data.error || `Server error (${response.status})`;
                console.error('Server returned error:', errorMsg);
                setError(errorMsg);
                console.error('Full error data:', data);
            }
        } catch (error: any) {
            console.error('=== EXCEPTION CAUGHT ===');
            console.error('Error Type:', error.constructor.name);
            console.error('Error Message:', error.message);
            console.error('Error Stack:', error.stack);

            if (error.message?.includes('fetch')) {
                setError('Cannot connect to server - is the API running?');
            } else if (error.message?.includes('JSON')) {
                setError('Invalid server response');
            } else {
                setError(`Network error: ${error.message}`);
            }
        } finally {
            setLoading(false);
        }
    };

    if (feedbackGiven) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center gap-2 text-green-600 dark:text-green-400"
            >
                <CheckCircle className="w-5 h-5" />
                <span className="text-sm font-medium">Thank you for your feedback!</span>
            </motion.div>
        );
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MessageSquare className="w-4 h-4" />
                <span>Was this prediction correct?</span>
            </div>

            {error && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3"
                >
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                </motion.div>
            )}

            <div className="flex gap-3">
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                        const actualLabel = prediction === 'Fraud' ? 'Fraud' : 'Legitimate';
                        submitFeedback(actualLabel);
                    }}
                    disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-500/10 hover:bg-green-500/20 text-green-600 dark:text-green-400 rounded-lg border border-green-500/20 transition-colors disabled:opacity-50"
                >
                    <ThumbsUp className="w-4 h-4" />
                    <span className="text-sm font-medium">
                        {loading ? 'Submitting...' : 'Yes, Correct'}
                    </span>
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                        const actualLabel = prediction === 'Fraud' ? 'Legitimate' : 'Fraud';
                        setShowNotes(true); // Show notes field for incorrect predictions
                    }}
                    disabled={loading}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 rounded-lg border border-red-500/20 transition-colors disabled:opacity-50"
                >
                    <ThumbsDown className="w-4 h-4" />
                    <span className="text-sm font-medium">No, Wrong</span>
                </motion.button>
            </div>

            <AnimatePresence>
                {showNotes && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="space-y-2"
                    >
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Optional: Why was the prediction incorrect?"
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none"
                            rows={3}
                        />
                        <div className="flex gap-2">
                            <button
                                onClick={() => {
                                    const actualLabel = prediction === 'Fraud' ? 'Legitimate' : 'Fraud';
                                    submitFeedback(actualLabel);
                                }}
                                disabled={loading}
                                className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 text-sm font-medium"
                            >
                                {loading ? 'Submitting...' : 'Submit Feedback'}
                            </button>
                            <button
                                onClick={() => setShowNotes(false)}
                                disabled={loading}
                                className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors text-sm"
                            >
                                Cancel
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
