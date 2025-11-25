import { useState, useEffect } from 'react';
import { History, Search, Trash2, Clock, Code, FileText, AlertCircle } from 'lucide-react';
import { getQueryHistory, deleteQuery, clearHistory, searchHistory } from '../utils/queryHistory';
import { formatDistanceToNow } from 'date-fns';

function QueryHistory() {
  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    const data = getQueryHistory();
    setHistory(data);
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      const results = searchHistory(query);
      setHistory(results);
    } else {
      loadHistory();
    }
  };

  const handleDelete = (id) => {
    deleteQuery(id);
    loadHistory();
    if (selectedQuery?.id === id) {
      setSelectedQuery(null);
    }
  };

  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to clear all query history?')) {
      clearHistory();
      loadHistory();
      setSelectedQuery(null);
      setShowDeleteConfirm(false);
    }
  };

  const handleQueryClick = (query) => {
    setSelectedQuery(query);
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Query History</h1>
          <p className="text-gray-600">
            View and manage your previous queries. History is stored locally in your browser.
          </p>
        </div>
        {history.length > 0 && (
          <button
            onClick={handleClearAll}
            className="btn-secondary flex items-center"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear All
          </button>
        )}
      </div>

      {/* Search Bar */}
      {history.length > 0 && (
        <div className="card">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search query history..."
              className="input-field pl-12"
            />
          </div>
        </div>
      )}

      {history.length === 0 ? (
        <div className="card text-center py-12">
          <History className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Query History</h3>
          <p className="text-gray-500">
            Your query history will appear here after you run some queries on the home page.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* History List */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <History className="h-5 w-5 text-primary-600 mr-2" />
                  <h2 className="text-lg font-semibold text-gray-900">Queries</h2>
                </div>
                <span className="bg-primary-100 text-primary-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                  {history.length}
                </span>
              </div>

              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {history.map((query) => (
                  <div
                    key={query.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
                      selectedQuery?.id === query.id
                        ? 'bg-primary-50 border-primary-300 shadow-sm'
                        : 'bg-white border-gray-200 hover:border-primary-200 hover:bg-gray-50'
                    }`}
                    onClick={() => handleQueryClick(query)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
                          {query.question}
                        </p>
                        <div className="flex items-center text-xs text-gray-500">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatDistanceToNow(new Date(query.timestamp), { addSuffix: true })}
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(query.id);
                        }}
                        className="ml-2 text-red-500 hover:text-red-700 transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Query Details */}
          <div className="lg:col-span-2">
            {!selectedQuery ? (
              <div className="card text-center py-12">
                <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Query Selected</h3>
                <p className="text-gray-500">
                  Select a query from the list to view its details
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Question */}
                <div className="card">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Question</h3>
                  <p className="text-lg text-gray-900">{selectedQuery.question}</p>
                  <div className="flex items-center text-sm text-gray-500 mt-3 pt-3 border-t">
                    <Clock className="h-4 w-4 mr-1" />
                    {new Date(selectedQuery.timestamp).toLocaleString()}
                  </div>
                </div>

                {/* Summary */}
                {selectedQuery.summary && (
                  <div className="card">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">AI Summary</h3>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-gray-800 leading-relaxed">{selectedQuery.summary}</p>
                    </div>
                  </div>
                )}

                {/* Explanation */}
                {selectedQuery.explanation && (
                  <div className="card">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Query Explanation
                    </h3>
                    <p className="text-gray-600">{selectedQuery.explanation}</p>
                  </div>
                )}

                {/* Cypher Query */}
                {selectedQuery.cypher_query && (
                  <div className="card">
                    <div className="flex items-center mb-2">
                      <Code className="h-4 w-4 text-gray-700 mr-2" />
                      <h3 className="text-sm font-medium text-gray-700">Generated Cypher</h3>
                    </div>
                    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                      <code>{selectedQuery.cypher_query}</code>
                    </pre>
                  </div>
                )}

                {/* SQL Query */}
                {selectedQuery.sql_query && (
                  <div className="card">
                    <div className="flex items-center mb-2">
                      <Code className="h-4 w-4 text-gray-700 mr-2" />
                      <h3 className="text-sm font-medium text-gray-700">Equivalent SQL Query</h3>
                    </div>
                    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                      <code>{selectedQuery.sql_query}</code>
                    </pre>
                  </div>
                )}

                {/* Results */}
                {selectedQuery.results && selectedQuery.results.length > 0 && (
                  <div className="card">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">
                      Results ({selectedQuery.results.length} records)
                    </h3>
                    <div className="table-container">
                      <table className="data-table">
                        <thead>
                          <tr>
                            {Object.keys(selectedQuery.results[0]).map((key) => (
                              <th key={key}>{key}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {selectedQuery.results.slice(0, 10).map((row, idx) => (
                            <tr key={idx}>
                              {Object.values(row).map((value, vidx) => (
                                <td key={vidx}>
                                  {typeof value === 'object'
                                    ? JSON.stringify(value)
                                    : String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {selectedQuery.results.length > 10 && (
                      <p className="text-sm text-gray-500 mt-2 text-center">
                        Showing first 10 of {selectedQuery.results.length} results
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default QueryHistory;
