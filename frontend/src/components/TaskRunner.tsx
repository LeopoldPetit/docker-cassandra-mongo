import { useState } from 'react'
import axios from 'axios'
import { 
  Play, 
  Search, 
  User, 
  TrendingUp, 
  Loader2,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

interface TaskResult {
  task: string
  params: Record<string, unknown>
  databases: Record<string, DatabaseResult>
}

interface DatabaseResult {
  status: string
  count?: number
  execution_time_ms?: number
  note?: string
  error?: string
  aggregations?: Record<string, AggregationResult>
  sample_data?: unknown[]
}

interface AggregationResult {
  count: number
  avg_duration: number
  min_duration: number
  max_duration: number
}

const tasks = [
  {
    id: 'task1',
    name: 'Tâche 1 - Recherche Full-Text',
    description: 'Recherche ERROR_404 avec "critique" dans la description',
    icon: Search,
    endpoint: '/task1',
    defaultParams: {
      event_type: 'ERROR_404',
      search_text: 'critique',
      date_start: '2025-10-01',
      date_end: '2025-10-31'
    }
  },
  {
    id: 'task2',
    name: 'Tâche 2 - Accès Ciblé',
    description: '100 derniers logs d\'un utilisateur',
    icon: User,
    endpoint: '/task2',
    defaultParams: {
      user_id: 10,
      limit: 100
    }
  },
  {
    id: 'task3',
    name: 'Tâche 3 - Agrégation',
    description: 'Temps de session moyen par type d\'événement',
    icon: TrendingUp,
    endpoint: '/task3',
    defaultParams: {
      event_types: ['PURCHASE', 'ADD_TO_CART']
    }
  }
]

export function TaskRunner() {
  const [loading, setLoading] = useState<string | null>(null)
  const [results, setResults] = useState<Record<string, TaskResult>>({})
  const [error, setError] = useState<string | null>(null)

  const runTask = async (taskId: string, endpoint: string, params: Record<string, unknown>) => {
    setLoading(taskId)
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}${endpoint}`, params)
      setResults(prev => ({ ...prev, [taskId]: response.data }))
    } catch (err) {
      setError(`Erreur lors de l'exécution: ${err instanceof Error ? err.message : 'Erreur inconnue'}`)
    } finally {
      setLoading(null)
    }
  }

  const runAllTasks = async () => {
    setLoading('all')
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}/all-tasks`, {})
      setResults({
        task1: response.data.task1,
        task2: response.data.task2,
        task3: response.data.task3
      })
    } catch (err) {
      setError(`Erreur: ${err instanceof Error ? err.message : 'Erreur inconnue'}`)
    } finally {
      setLoading(null)
    }
  }

  const getChartData = (taskId: string) => {
    const result = results[taskId]
    if (!result) return []
    
    return Object.entries(result.databases).map(([db, data]) => ({
      name: db.charAt(0).toUpperCase() + db.slice(1),
      count: data.count || 0,
      time: data.execution_time_ms || 0
    }))
  }

  const getAggregationChartData = (taskId: string) => {
    const result = results[taskId]
    if (!result) return []
    
    const data: { name: string; [key: string]: number | string }[] = []
    
    Object.entries(result.databases).forEach(([db, dbData]) => {
      if (dbData.aggregations) {
        Object.entries(dbData.aggregations).forEach(([eventType, agg]) => {
          const existing = data.find(d => d.name === eventType)
          if (existing) {
            existing[db] = agg.avg_duration
          } else {
            data.push({
              name: eventType,
              [db]: agg.avg_duration
            })
          }
        })
      }
    })
    
    return data
  }

  return (
    <div className="task-runner">
      <div className="task-header">
        <h2>Exécution des Tâches</h2>
        <button 
          className="btn btn-primary"
          onClick={runAllTasks}
          disabled={loading !== null}
        >
          {loading === 'all' ? <Loader2 className="spin" size={18} /> : <Play size={18} />}
          Exécuter Toutes
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <XCircle size={18} />
          {error}
        </div>
      )}

      <div className="tasks-grid">
        {tasks.map(task => (
          <div key={task.id} className="task-card">
            <div className="task-card-header">
              <div className="task-icon">
                <task.icon size={24} />
              </div>
              <div className="task-info">
                <h3>{task.name}</h3>
                <p>{task.description}</p>
              </div>
              <button 
                className="btn btn-secondary"
                onClick={() => runTask(task.id, task.endpoint, task.defaultParams)}
                disabled={loading !== null}
              >
                {loading === task.id ? <Loader2 className="spin" size={16} /> : <Play size={16} />}
              </button>
            </div>

            {results[task.id] && (
              <div className="task-results">
                <div className="results-grid">
                  {Object.entries(results[task.id].databases).map(([db, data]) => (
                    <div key={db} className={`db-result ${data.status}`}>
                      <div className="db-header">
                        {data.status === 'success' ? (
                          <CheckCircle size={16} className="success" />
                        ) : (
                          <XCircle size={16} className="error" />
                        )}
                        <span className="db-name">{db}</span>
                      </div>
                      {data.status === 'success' && (
                        <div className="db-stats">
                          {data.count !== undefined && (
                            <div className="stat">
                              <span className="stat-value">{data.count}</span>
                              <span className="stat-label">résultats</span>
                            </div>
                          )}
                          {data.execution_time_ms !== undefined && (
                            <div className="stat">
                              <Clock size={14} />
                              <span className="stat-value">{data.execution_time_ms}</span>
                              <span className="stat-label">ms</span>
                            </div>
                          )}
                        </div>
                      )}
                      {data.note && <p className="db-note">{data.note}</p>}
                      {data.error && <p className="db-error">{data.error}</p>}
                    </div>
                  ))}
                </div>

                {task.id !== 'task3' && getChartData(task.id).length > 0 && (
                  <div className="chart-container">
                    <h4>Comparaison des performances</h4>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={getChartData(task.id)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                        <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                        <Tooltip />
                        <Legend />
                        <Bar yAxisId="left" dataKey="time" name="Temps (ms)" fill="#8884d8" />
                        <Bar yAxisId="right" dataKey="count" name="Résultats" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {task.id === 'task3' && getAggregationChartData(task.id).length > 0 && (
                  <div className="chart-container">
                    <h4>Durée moyenne par type d'événement</h4>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={getAggregationChartData(task.id)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="mongodb" name="MongoDB" fill="#4db33d" />
                        <Bar dataKey="elasticsearch" name="Elasticsearch" fill="#f9b116" />
                        <Bar dataKey="cassandra" name="Cassandra" fill="#1287b1" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
