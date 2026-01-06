/** 
 * API Configuration
 * Centralized API URL management for the frontend
 */

// Get API URL from environment variable
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// Log it for debugging (will show in browser console)
if (typeof window !== 'undefined') {
    console.log('🔗 API Configuration:');
    console.log('  - Environment Variable:', process.env.NEXT_PUBLIC_API_URL);
    console.log('  - Actual API URL:', API_BASE_URL);
}

export default API_BASE_URL;
