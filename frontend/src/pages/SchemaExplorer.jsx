import { useState, useEffect } from 'react';
import { Search, Database, Table, ChevronRight, Tag, MapPin, Loader2 } from 'lucide-react';
import { getTables, getTableDetails, searchTables } from '../services/api';

function SchemaExplorer() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableDetails, setTableDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);

  useEffect(() => {
    loadTables();
  }, []);

  const loadTables = async () => {
    try {
      setLoading(true);
      const data = await getTables();
      setTables(data.tables || []);
    } catch (error) {
      console.error('Failed to load tables:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTableClick = async (tableName) => {
    setSelectedTable(tableName);
    setDetailsLoading(true);
    setTableDetails(null);

    try {
      const details = await getTableDetails(tableName);
      setTableDetails(details);
    } catch (error) {
      console.error('Failed to load table details:', error);
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);

    if (!query.trim()) {
      setSearchResults(null);
      return;
    }

    try {
      const results = await searchTables(query);
      setSearchResults(results.tables || []);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    }
  };

  const displayTables = searchResults !== null ? searchResults : tables;

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Schema Explorer</h1>
        <p className="text-gray-600">
          Browse and explore the metadata catalog. Click on any table to view detailed information.
        </p>
      </div>

      {/* Search Bar */}
      <div className="card">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search tables by name or description..."
            className="input-field pl-12"
          />
        </div>
        {searchQuery && (
          <p className="text-sm text-gray-500 mt-2">
            {displayTables.length} table(s) found
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tables List */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="flex items-center mb-4">
              <Database className="h-5 w-5 text-primary-600 mr-2" />
              <h2 className="text-lg font-semibold text-gray-900">Tables</h2>
              <span className="ml-auto bg-primary-100 text-primary-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                {displayTables.length}
              </span>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="animate-spin h-8 w-8 text-primary-600" />
              </div>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {displayTables.map((table) => (
                  <button
                    key={table.name}
                    onClick={() => handleTableClick(table.name)}
                    className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${
                      selectedTable === table.name
                        ? 'bg-primary-50 border-primary-300 shadow-sm'
                        : 'bg-white border-gray-200 hover:border-primary-200 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center min-w-0 flex-1">
                        <Table className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
                        <span className="font-medium text-gray-900 truncate">
                          {table.name}
                        </span>
                      </div>
                      <ChevronRight
                        className={`h-4 w-4 text-gray-400 flex-shrink-0 transition-transform duration-200 ${
                          selectedTable === table.name ? 'transform rotate-90' : ''
                        }`}
                      />
                    </div>
                    {table.description && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                        {table.description}
                      </p>
                    )}
                  </button>
                ))}

                {displayTables.length === 0 && (
                  <p className="text-center text-gray-500 py-8">No tables found</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Table Details */}
        <div className="lg:col-span-2">
          {!selectedTable ? (
            <div className="card text-center py-12">
              <Database className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Table Selected</h3>
              <p className="text-gray-500">
                Select a table from the list to view its details
              </p>
            </div>
          ) : detailsLoading ? (
            <div className="card">
              <div className="flex items-center justify-center py-12">
                <Loader2 className="animate-spin h-8 w-8 text-primary-600" />
              </div>
            </div>
          ) : tableDetails ? (
            <div className="space-y-6">
              {/* Table Info */}
              <div className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{tableDetails.name}</h2>
                    {tableDetails.description && (
                      <p className="text-gray-600 mt-2">{tableDetails.description}</p>
                    )}
                  </div>
                </div>

                {/* Regions */}
                {tableDetails.regions && tableDetails.regions.length > 0 && (
                  <div className="flex items-center space-x-2 mt-4">
                    <MapPin className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-600">Regions:</span>
                    <div className="flex flex-wrap gap-2">
                      {tableDetails.regions.map((region) => (
                        <span
                          key={region}
                          className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full"
                        >
                          {region}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Columns */}
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Columns ({tableDetails.columns?.length || 0})
                </h3>

                <div className="space-y-3">
                  {tableDetails.columns && tableDetails.columns.length > 0 ? (
                    tableDetails.columns
                      .filter((col) => col.name) // Filter out null/empty columns
                      .map((column, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                              <div className="h-8 w-8 bg-primary-100 rounded-lg flex items-center justify-center">
                                <span className="text-xs font-medium text-primary-700">
                                  {column.data_type?.substring(0, 3).toUpperCase() || 'COL'}
                                </span>
                              </div>
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">{column.name}</p>
                              {column.data_type && (
                                <p className="text-sm text-gray-500">{column.data_type}</p>
                              )}
                            </div>
                          </div>

                          {/* CDE Badge */}
                          {column.is_cde && (
                            <div className="flex items-center space-x-2">
                              <Tag className="h-4 w-4 text-red-500" />
                              <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                                CDE
                              </span>
                              {column.cde_name && (
                                <span className="text-xs text-gray-500">
                                  ({column.cde_name})
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      ))
                  ) : (
                    <p className="text-center text-gray-500 py-4">No columns found</p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="card text-center py-12">
              <p className="text-red-600">Failed to load table details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SchemaExplorer;
