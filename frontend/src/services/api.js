/**
 * API Service Layer
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios';

// Base API URL - proxied through Vite
const API_BASE_URL = '/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    console.error('API Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

// API Methods

/**
 * Ask a natural language question
 * @param {string} question - The question to ask
 * @returns {Promise} Response with cypher, results, and summary
 */
export const askQuestion = async (question) => {
  try {
    const response = await apiClient.post('/ask', { question });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to process question: ${error.message}`);
  }
};

/**
 * Execute a raw Cypher query
 * @param {string} cypher - The Cypher query to execute
 * @returns {Promise} Query results
 */
export const runCypher = async (cypher) => {
  try {
    const response = await apiClient.post('/query/cypher', { cypher });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to execute Cypher: ${error.message}`);
  }
};

/**
 * Get all tables in the schema
 * @returns {Promise} List of tables with columns
 */
export const getTables = async () => {
  try {
    const response = await apiClient.get('/schema/tables');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch tables: ${error.message}`);
  }
};

/**
 * Get detailed information about a specific table
 * @param {string} tableName - Name of the table
 * @returns {Promise} Table details including columns, CDEs, and regions
 */
export const getTableDetails = async (tableName) => {
  try {
    const response = await apiClient.get(`/schema/table/${tableName}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch table details: ${error.message}`);
  }
};

/**
 * Get data lineage for a table
 * @param {string} tableName - Name of the table
 * @param {number} depth - Lineage depth (1-5)
 * @returns {Promise} Nodes and edges for lineage graph
 */
export const getLineage = async (tableName, depth = 2) => {
  try {
    const response = await apiClient.get(`/lineage/${tableName}`, {
      params: { depth },
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch lineage: ${error.message}`);
  }
};

/**
 * Search tables by name or description
 * @param {string} query - Search query
 * @returns {Promise} Matching tables
 */
export const searchTables = async (query) => {
  try {
    const response = await apiClient.get('/search/tables', {
      params: { q: query },
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to search tables: ${error.message}`);
  }
};

/**
 * Get database statistics
 * @returns {Promise} Stats about the database
 */
export const getStats = async () => {
  try {
    const response = await apiClient.get('/stats');
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch stats: ${error.message}`);
  }
};

/**
 * Health check
 * @returns {Promise} API health status
 */
export const healthCheck = async () => {
  try {
    const response = await axios.get('http://localhost:8000/');
    return response.data;
  } catch (error) {
    throw new Error('API is not reachable');
  }
};

export default {
  askQuestion,
  runCypher,
  getTables,
  getTableDetails,
  getLineage,
  searchTables,
  getStats,
  healthCheck,
};
