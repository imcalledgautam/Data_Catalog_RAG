import { useState, useEffect } from 'react';
import { Search, Loader2, AlertCircle, CheckCircle, Copy, Sparkles } from 'lucide-react';
import { askQuestion, getStats } from '../services/api';
import { saveQuery } from '../utils/queryHistory';

const EXAMPLE_QUERIES = [
  "Show me all clients with loan amounts greater than $50,000",
  "What are the different account types and their interest rates?",
  "List all card transactions over $1,000 in the last month",
  "Which branches have the most employees?",
  "Show me clients who have both credit cards and loans",
  "What are the most common customer support issues?",
];

function HomePage() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Load stats on mount
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data.stats);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await askQuestion(question);
      setResult(data);
      setActiveTab('summary');

      // Save to history
      saveQuery({
        question,
        cypher_query: data.cypher_query,
        explanation: data.explanation,
        summary: data.summary,
        results: data.results,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuestion(exampleQuery);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Ask Questions About Your Bank Data
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Use natural language to query your bank's data catalog. Our AI will convert your
          question into a Cypher query and return the results.
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(stats).map(([key, value]) => (
            <div key={key} className="card text-center">
              <p className="text-3xl font-bold text-primary-600">{value.toLocaleString()}</p>
              <p className="text-sm text-gray-600 capitalize mt-1">{key}</p>
            </div>
          ))}
        </div>
      )}

      {/* Search Bar */}
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about the data..."
              className="input-field pl-12 pr-4"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="btn-primary w-full mt-4 flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin h-5 w-5 mr-2" />
                Processing...
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5 mr-2" />
                Ask Question
              </>
            )}
          </button>
        </form>

        {/* Example Queries */}
        <div className="mt-6">
          <p className="text-sm font-medium text-gray-700 mb-3">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-full transition-colors duration-200"
                disabled={loading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="card border-red-200 bg-red-50">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="card fade-in">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-500 mr-2" />
            <h2 className="text-xl font-bold text-gray-900">Results</h2>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-4">
            <nav className="flex space-x-8">
              {['summary', 'results', 'cypher'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm capitalize transition-colors duration-200 ${
                    activeTab === tab
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-4">
            {/* Summary Tab */}
            {activeTab === 'summary' && (
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">AI Summary</h3>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-gray-800 leading-relaxed">{result.summary}</p>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Query Explanation</h3>
                  <p className="text-gray-600">{result.explanation}</p>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{result.results.length} records returned</span>
                  <span>Executed at {new Date(result.timestamp).toLocaleString()}</span>
                </div>
              </div>
            )}

            {/* Results Tab */}
            {activeTab === 'results' && (
              <div>
                {result.results.length > 0 ? (
                  <div className="table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          {Object.keys(result.results[0]).map((key) => (
                            <th key={key}>{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.results.map((row, idx) => (
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
                ) : (
                  <p className="text-gray-500 text-center py-8">No results found</p>
                )}
              </div>
            )}

            {/* Cypher Tab */}
            {activeTab === 'cypher' && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-700">Generated Cypher Query</h3>
                  <button
                    onClick={() => copyToClipboard(result.cypher_query)}
                    className="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors duration-200"
                  >
                    <Copy className="h-4 w-4 mr-1" />
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{result.cypher_query}</code>
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;
