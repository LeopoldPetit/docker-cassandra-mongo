import { useState } from 'react'
import './App.css'
import { TaskRunner } from './components/TaskRunner'
import { HealthCheck } from './components/HealthCheck'
import { DataManager } from './components/DataManager'
import { Database, Zap, BarChart3, Settings } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState<'health' | 'tasks' | 'data'>('tasks')

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Database size={32} />
            <h1>TP NoSQL Dashboard</h1>
          </div>
          <p className="subtitle">Comparaison Cassandra • MongoDB • Elasticsearch</p>
        </div>
      </header>

      <nav className="nav">
        <button 
          className={`nav-btn ${activeTab === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveTab('tasks')}
        >
          <Zap size={18} />
          Tâches
        </button>
        <button 
          className={`nav-btn ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => setActiveTab('health')}
        >
          <BarChart3 size={18} />
          Santé
        </button>
        <button 
          className={`nav-btn ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
        >
          <Settings size={18} />
          Données
        </button>
      </nav>

      <main className="main">
        {activeTab === 'tasks' && <TaskRunner />}
        {activeTab === 'health' && <HealthCheck />}
        {activeTab === 'data' && <DataManager />}
      </main>

      <footer className="footer">
        <p>TP NoSQL - Cassandra, MongoDB, Elasticsearch</p>
      </footer>
    </div>
  )
}

export default App
