import { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Search, Network, Loader2, AlertCircle } from 'lucide-react';
import { getLineage, getTables } from '../services/api';

const nodeColor = (type) => {
  switch (type) {
    case 'center':
      return '#2563eb'; // blue-600
    case 'related':
      return '#059669'; // green-600
    default:
      return '#6b7280'; // gray-500
  }
};

function LineageViewer() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [depth, setDepth] = useState(2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    loadTables();
  }, []);

  const loadTables = async () => {
    try {
      const data = await getTables();
      setTables(data.tables || []);
    } catch (error) {
      console.error('Failed to load tables:', error);
    }
  };

  const loadLineage = async () => {
    if (!selectedTable) {
      setError('Please select a table');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getLineage(selectedTable, depth);

      // Convert lineage data to React Flow format
      const flowNodes = data.nodes.map((node, index) => ({
        id: node.id,
        data: {
          label: (
            <div className="px-4 py-2">
              <div className="font-semibold">{node.label}</div>
              <div className="text-xs text-gray-500 capitalize">{node.type}</div>
            </div>
          ),
        },
        position: calculateNodePosition(index, data.nodes.length),
        style: {
          background: nodeColor(node.type),
          color: 'white',
          border: '2px solid #fff',
          borderRadius: '8px',
          fontSize: '12px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        },
      }));

      const flowEdges = data.edges.map((edge, index) => ({
        id: `edge-${index}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: true,
        label: edge.type,
        labelStyle: { fontSize: '10px', fill: '#6b7280' },
        style: { stroke: '#9ca3af' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#9ca3af',
        },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateNodePosition = (index, total) => {
    // Simple circular layout
    const radius = 250;
    const angle = (index / total) * 2 * Math.PI;
    return {
      x: 400 + radius * Math.cos(angle),
      y: 300 + radius * Math.sin(angle),
    };
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Data Lineage Viewer</h1>
        <p className="text-gray-600">
          Visualize data lineage to understand upstream and downstream dependencies between tables.
        </p>
      </div>

      {/* Controls */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Table Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Table
            </label>
            <div className="relative">
              <Network className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                value={selectedTable}
                onChange={(e) => setSelectedTable(e.target.value)}
                className="input-field pl-10 appearance-none"
              >
                <option value="">Choose a table...</option>
                {tables.map((table) => (
                  <option key={table.name} value={table.name}>
                    {table.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Depth Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lineage Depth
            </label>
            <select
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="input-field"
            >
              <option value="1">1 Level</option>
              <option value="2">2 Levels</option>
              <option value="3">3 Levels</option>
              <option value="4">4 Levels</option>
              <option value="5">5 Levels</option>
            </select>
          </div>

          {/* Load Button */}
          <div className="flex items-end">
            <button
              onClick={loadLineage}
              disabled={loading || !selectedTable}
              className="btn-primary w-full flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  Loading...
                </>
              ) : (
                <>
                  <Search className="h-5 w-5 mr-2" />
                  Load Lineage
                </>
              )}
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-2">Legend:</p>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center">
              <div className="w-4 h-4 rounded" style={{ background: nodeColor('center') }}></div>
              <span className="ml-2 text-sm text-gray-600">Selected Table</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded" style={{ background: nodeColor('related') }}></div>
              <span className="ml-2 text-sm text-gray-600">Related Tables</span>
            </div>
            <div className="flex items-center">
              <div className="w-12 h-0.5 bg-gray-400"></div>
              <span className="ml-2 text-sm text-gray-600">Data Flow</span>
            </div>
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

      {/* Graph Visualization */}
      <div className="card p-0 overflow-hidden" style={{ height: '600px' }}>
        {nodes.length > 0 ? (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#e5e7eb" gap={16} />
            <Controls />
            <MiniMap
              nodeColor={(node) => node.style.background}
              maskColor="rgba(0, 0, 0, 0.1)"
            />
          </ReactFlow>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Network className="h-16 w-16 text-gray-300 mb-4" />
            <p className="text-lg font-medium">No Lineage Data</p>
            <p className="text-sm mt-2">Select a table and click "Load Lineage" to visualize</p>
          </div>
        )}
      </div>

      {/* Stats */}
      {nodes.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <div className="card text-center">
            <p className="text-3xl font-bold text-primary-600">{nodes.length}</p>
            <p className="text-sm text-gray-600 mt-1">Tables</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-primary-600">{edges.length}</p>
            <p className="text-sm text-gray-600 mt-1">Relationships</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-primary-600">{depth}</p>
            <p className="text-sm text-gray-600 mt-1">Depth Levels</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default LineageViewer;
