import { useState, useEffect } from 'react';
import { Database, Trash2, RefreshCw, Loader2, CheckCircle2, XCircle, Plus } from 'lucide-react';
import axios from 'axios';

interface DataStats {
  cassandra: number | string;
  mongodb: number | string;
  elasticsearch: number | string;
}

interface InsertResult {
  databases: {
    cassandra: { status: string; inserted?: number; error?: string };
    mongodb: { status: string; inserted?: number; error?: string };
    elasticsearch: { status: string; inserted?: number; error?: string };
  };
  requested: number;
}

export function DataManager() {
  const [stats, setStats] = useState<DataStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [numLogs, setNumLogs] = useState(10000);
  const [result, setResult] = useState<InsertResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/data/stats');
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError('Erreur lors de la récupération des stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const clearAllData = async () => {
    if (!confirm('⚠️ Voulez-vous vraiment vider TOUTES les bases de données ?')) return;
    
    setClearing(true);
    setError(null);
    try {
      await axios.post('/api/data/clear');
      await fetchStats();
      setResult(null);
    } catch (err) {
      setError('Erreur lors du vidage des bases');
    } finally {
      setClearing(false);
    }
  };

  const generateData = async () => {
    setGenerating(true);
    setProgress(0);
    setError(null);
    setResult(null);

    // Simuler une progression
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 15;
      });
    }, 500);

    try {
      const response = await axios.post('/api/data/generate', {
        num_logs: numLogs,
        num_users: Math.min(numLogs / 10, 5000),
        num_products: 100
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      setResult(response.data);
      await fetchStats();
      
      setTimeout(() => setProgress(0), 2000);
    } catch (err) {
      clearInterval(progressInterval);
      setProgress(0);
      setError('Erreur lors de la génération des données');
    } finally {
      setGenerating(false);
    }
  };

  const formatNumber = (num: number | string) => {
    if (typeof num === 'string') return num;
    return num.toLocaleString('fr-FR');
  };

  return (
    <div className="data-manager">
      <div className="data-header">
        <h2><Database size={24} /> Gestion des Données</h2>
        <button 
          className="btn btn-secondary" 
          onClick={fetchStats} 
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          Actualiser
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <XCircle size={20} />
          {error}
        </div>
      )}

      {/* Stats actuelles */}
      <div className="stats-section">
        <h3>📊 Données actuelles</h3>
        <div className="stats-grid">
          <div className="stat-card cassandra">
            <div className="stat-db-name">Cassandra</div>
            <div className="stat-count">
              {loading ? <Loader2 size={20} className="spin" /> : formatNumber(stats?.cassandra ?? 0)}
            </div>
            <div className="stat-label">documents</div>
          </div>
          <div className="stat-card mongodb">
            <div className="stat-db-name">MongoDB</div>
            <div className="stat-count">
              {loading ? <Loader2 size={20} className="spin" /> : formatNumber(stats?.mongodb ?? 0)}
            </div>
            <div className="stat-label">documents</div>
          </div>
          <div className="stat-card elasticsearch">
            <div className="stat-db-name">Elasticsearch</div>
            <div className="stat-count">
              {loading ? <Loader2 size={20} className="spin" /> : formatNumber(stats?.elasticsearch ?? 0)}
            </div>
            <div className="stat-label">documents</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="actions-section">
        <div className="action-card">
          <h3><Trash2 size={20} /> Vider les bases</h3>
          <p>Supprime toutes les données de Cassandra, MongoDB et Elasticsearch</p>
          <button 
            className="btn btn-danger" 
            onClick={clearAllData}
            disabled={clearing || generating}
          >
            {clearing ? (
              <>
                <Loader2 size={16} className="spin" />
                Suppression...
              </>
            ) : (
              <>
                <Trash2 size={16} />
                Vider toutes les bases
              </>
            )}
          </button>
        </div>

        <div className="action-card">
          <h3><Plus size={20} /> Générer des données</h3>
          <p>Génère et insère des logs e-commerce dans les 3 bases</p>
          
          <div className="input-group">
            <label>Nombre de logs à générer :</label>
            <input 
              type="number" 
              value={numLogs}
              onChange={(e) => setNumLogs(Math.max(100, Math.min(500000, parseInt(e.target.value) || 0)))}
              min="100"
              max="500000"
              step="1000"
              disabled={generating}
            />
          </div>

          <div className="presets">
            {[1000, 10000, 50000, 100000, 250000].map(n => (
              <button 
                key={n}
                className={`preset-btn ${numLogs === n ? 'active' : ''}`}
                onClick={() => setNumLogs(n)}
                disabled={generating}
              >
                {formatNumber(n)}
              </button>
            ))}
          </div>

          {generating && (
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="progress-text">
                {progress < 100 ? `Génération en cours... ${Math.round(progress)}%` : 'Terminé !'}
              </div>
            </div>
          )}

          <button 
            className="btn btn-primary btn-large" 
            onClick={generateData}
            disabled={generating || clearing}
          >
            {generating ? (
              <>
                <Loader2 size={16} className="spin" />
                Génération en cours...
              </>
            ) : (
              <>
                <Plus size={16} />
                Générer {formatNumber(numLogs)} logs
              </>
            )}
          </button>
        </div>
      </div>

      {/* Résultat */}
      {result && (
        <div className="result-section">
          <h3><CheckCircle2 size={20} className="success" /> Génération terminée</h3>
          <div className="result-grid">
            {Object.entries(result.databases).map(([db, info]) => (
              <div key={db} className={`result-card ${info.status}`}>
                <div className="result-db">{db}</div>
                {info.status === 'success' ? (
                  <div className="result-count">
                    <CheckCircle2 size={16} className="success" />
                    {formatNumber(info.inserted ?? 0)} insérés
                  </div>
                ) : (
                  <div className="result-error">
                    <XCircle size={16} />
                    {info.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
