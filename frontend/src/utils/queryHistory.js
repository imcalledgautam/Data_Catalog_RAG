/**
 * Query History Manager
 * Manages query history using localStorage
 */

const HISTORY_KEY = 'query_history';
const MAX_HISTORY_ITEMS = 50;

/**
 * Save a query to history
 * @param {Object} queryData - Query data to save
 */
export const saveQuery = (queryData) => {
  try {
    const history = getQueryHistory();
    const newEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      ...queryData,
    };

    // Add to beginning of array
    history.unshift(newEntry);

    // Limit history size
    const trimmedHistory = history.slice(0, MAX_HISTORY_ITEMS);

    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmedHistory));
    return newEntry;
  } catch (error) {
    console.error('Failed to save query to history:', error);
    return null;
  }
};

/**
 * Get all query history
 * @returns {Array} Array of query history items
 */
export const getQueryHistory = () => {
  try {
    const history = localStorage.getItem(HISTORY_KEY);
    return history ? JSON.parse(history) : [];
  } catch (error) {
    console.error('Failed to load query history:', error);
    return [];
  }
};

/**
 * Get a specific query by ID
 * @param {number} id - Query ID
 * @returns {Object|null} Query object or null
 */
export const getQueryById = (id) => {
  try {
    const history = getQueryHistory();
    return history.find((item) => item.id === id) || null;
  } catch (error) {
    console.error('Failed to get query:', error);
    return null;
  }
};

/**
 * Delete a query from history
 * @param {number} id - Query ID to delete
 */
export const deleteQuery = (id) => {
  try {
    const history = getQueryHistory();
    const filtered = history.filter((item) => item.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('Failed to delete query:', error);
    return false;
  }
};

/**
 * Clear all query history
 */
export const clearHistory = () => {
  try {
    localStorage.removeItem(HISTORY_KEY);
    return true;
  } catch (error) {
    console.error('Failed to clear history:', error);
    return false;
  }
};

/**
 * Search query history
 * @param {string} searchTerm - Term to search for
 * @returns {Array} Filtered history items
 */
export const searchHistory = (searchTerm) => {
  try {
    const history = getQueryHistory();
    const term = searchTerm.toLowerCase();

    return history.filter((item) => {
      return (
        item.question?.toLowerCase().includes(term) ||
        item.cypher_query?.toLowerCase().includes(term) ||
        item.explanation?.toLowerCase().includes(term)
      );
    });
  } catch (error) {
    console.error('Failed to search history:', error);
    return [];
  }
};

export default {
  saveQuery,
  getQueryHistory,
  getQueryById,
  deleteQuery,
  clearHistory,
  searchHistory,
};
