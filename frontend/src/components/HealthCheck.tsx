import { useState, useEffect } from 'react'
import axios from 'axios'
import { RefreshCw, CheckCircle, XCircle, Loader2 } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

interface HealthStatus {
  api: string
  databases: {
    cassandra: string
    mongodb: string
    elasticsearch: string
  }
}

export function HealthCheck() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checkHealth = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.get(`${API_URL}/health`)
      setHealth(response.data)
    } catch (err) {
      setError(`Impossible de contacter l'API: ${err instanceof Error ? err.message : 'Erreur'}`)
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkHealth()
  }, [])

  const getStatusIcon = (status: string) => {
    if (status === 'ok') {
      return <CheckCircle className="status-icon success" size={24} />
    }
    return <XCircle className="status-icon error" size={24} />
  }

  const getStatusClass = (status: string) => {
    return status === 'ok' ? 'healthy' : 'unhealthy'
  }

  return (
    <div className="health-check">
      <div className="health-header">
        <h2>État des Services</h2>
        <button 
          className="btn btn-secondary"
          onClick={checkHealth}
          disabled={loading}
        >
          {loading ? <Loader2 className="spin" size={18} /> : <RefreshCw size={18} />}
          Rafraîchir
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <XCircle size={18} />
          {error}
        </div>
      )}

      {loading && !health && (
        <div className="loading-state">
          <Loader2 className="spin" size={48} />
          <p>Vérification des services...</p>
        </div>
      )}

      {health && (
        <div className="health-grid">
          <div className={`health-card ${getStatusClass(health.api)}`}>
            {getStatusIcon(health.api)}
            <div className="health-info">
              <h3>API Backend</h3>
              <p className="health-status">{health.api === 'ok' ? 'Opérationnel' : 'Erreur'}</p>
              <span className="health-url">localhost:5000</span>
            </div>
          </div>

          <div className={`health-card ${getStatusClass(health.databases.cassandra)}`}>
            {getStatusIcon(health.databases.cassandra)}
            <div className="health-info">
              <h3>Cassandra</h3>
              <p className="health-status">
                {health.databases.cassandra === 'ok' ? 'Connecté' : 'Déconnecté'}
              </p>
              <span className="health-url">localhost:9042</span>
            </div>
          </div>

          <div className={`health-card ${getStatusClass(health.databases.mongodb)}`}>
            {getStatusIcon(health.databases.mongodb)}
            <div className="health-info">
              <h3>MongoDB</h3>
              <p className="health-status">
                {health.databases.mongodb === 'ok' ? 'Connecté' : 'Déconnecté'}
              </p>
              <span className="health-url">localhost:27017</span>
            </div>
          </div>

          <div className={`health-card ${getStatusClass(health.databases.elasticsearch)}`}>
            {getStatusIcon(health.databases.elasticsearch)}
            <div className="health-info">
              <h3>Elasticsearch</h3>
              <p className="health-status">
                {health.databases.elasticsearch === 'ok' ? 'Connecté' : 'Déconnecté'}
              </p>
              <span className="health-url">localhost:9200</span>
            </div>
          </div>
        </div>
      )}

      <div className="services-info">
        <h3>Interfaces Web</h3>
        <div className="services-links">
          <a href="http://localhost:8081" target="_blank" rel="noopener noreferrer" className="service-link">
            <span className="service-name">Mongo Express</span>
            <span className="service-url">:8081</span>
          </a>
          <a href="http://localhost:5601" target="_blank" rel="noopener noreferrer" className="service-link">
            <span className="service-name">Kibana</span>
            <span className="service-url">:5601</span>
          </a>
          <a href="http://localhost:9200" target="_blank" rel="noopener noreferrer" className="service-link">
            <span className="service-name">Elasticsearch API</span>
            <span className="service-url">:9200</span>
          </a>
        </div>
      </div>
    </div>
  )
}
