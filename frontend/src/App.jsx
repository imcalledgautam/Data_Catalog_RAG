import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Database, Home, Network, History, BarChart3 } from 'lucide-react';
import HomePage from './pages/HomePage';
import SchemaExplorer from './pages/SchemaExplorer';
import LineageViewer from './pages/LineageViewer';
import QueryHistory from './pages/QueryHistory';

function Navigation() {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/schema', icon: Database, label: 'Schema Explorer' },
    { path: '/lineage', icon: Network, label: 'Lineage Viewer' },
    { path: '/history', icon: History, label: 'Query History' },
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Database className="h-8 w-8 text-primary-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">
              Bank Data Catalog
            </span>
          </div>

          {/* Navigation Links */}
          <div className="flex space-x-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`inline-flex items-center px-4 py-2 border-b-2 text-sm font-medium transition-colors duration-200 ${
                    isActive(item.path)
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/schema" element={<SchemaExplorer />} />
            <Route path="/lineage" element={<LineageViewer />} />
            <Route path="/history" element={<QueryHistory />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Bank Data Catalog - Text-to-Cypher POC
              </p>
              <div className="flex items-center space-x-4">
                <BarChart3 className="h-5 w-5 text-gray-400" />
                <span className="text-sm text-gray-500">
                  Powered by Neo4j & OpenAI GPT-4
                </span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
