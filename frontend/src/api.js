/**
 * API helper functions for communicating with the backend
 */
import axios from 'axios';

// API URL from environment variable or default to localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Send a message/question to the chatbot API
 * 
 * @param {string} question - The user's question
 * @returns {Promise<Object>} Response with answer and sources
 * @throws {Error} If the API request fails
 */
export const sendMessage = async (question) => {
  try {
    const response = await axios.post(`${API_URL}/api/chat`, {
      question: question
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    
    // Extract error message from response if available
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        'Failed to get response from server';
    
    throw new Error(errorMessage);
  }
};

/**
 * Check if the backend API is healthy
 * 
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/health`);
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw new Error('Backend server is not responding');
  }
};

/**
 * Download PDF with relevant act sections for a question
 * 
 * @param {string} question - The user's question
 * @returns {Promise<Blob>} PDF file as blob
 * @throws {Error} If the API request fails
 */
export const downloadPDF = async (question) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/download-pdf`,
      { question: question },
      {
        responseType: 'blob' // Important: receive binary data
      }
    );
    return response.data;
  } catch (error) {
    console.error('PDF download error:', error);
    
    // Extract error message from response if available
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        'Failed to download PDF';
    
    throw new Error(errorMessage);
  }
};

