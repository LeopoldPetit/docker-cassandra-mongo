# TP NoSQL - Dashboard React

Dashboard interactif pour le TP NoSQL comparant Cassandra, MongoDB et Elasticsearch.

## 🎯 Fonctionnalités

- **Health Check** : Statut en temps réel des 3 bases de données + API
- **Task Runner** : Exécution des 3 tâches de benchmark avec visualisation des résultats
- **Data Manager** : Génération et suppression des données depuis l'interface
- **Graphiques** : Visualisation comparative avec Recharts

## 🛠️ Technologies

- **React 18** + TypeScript
- **Vite** : Build tool ultra-rapide
- **Recharts** : Graphiques
- **Lucide React** : Icônes
- **Nginx** : Serveur de production avec proxy vers l'API

## 🚀 Développement

### Prérequis

- Node.js 18+
- L'API doit être en cours d'exécution sur le port 5050

### Installation

```bash
cd frontend
npm install
```

### Mode développement

```bash
npm run dev
```

Le frontend sera disponible sur http://localhost:5173 avec hot reload.

### Build production

```bash
npm run build
```

Les fichiers statiques seront générés dans le dossier `dist/`.

## 🐳 Docker

Le frontend est automatiquement déployé avec Docker Compose :

```bash
# Depuis la racine du projet
docker-compose up -d frontend
```

- **URL Production** : http://localhost:3000
- Le proxy Nginx redirige `/api/*` vers le backend sur le port 5050

## 📁 Structure

```
frontend/
├── Dockerfile          # Image Nginx multi-stage
├── nginx.conf          # Config proxy API
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
├── public/
│   └── vite.svg
└── src/
    ├── main.tsx        # Point d'entrée
    ├── App.tsx         # Composant principal
    ├── App.css         # Styles globaux
    ├── index.css       # Reset CSS
    ├── assets/
    └── components/
        ├── HealthCheck.tsx   # Statut des DBs
        ├── TaskRunner.tsx    # Exécution des tâches
        └── DataManager.tsx   # Gestion des données
```

## 🔌 API Backend

Le frontend communique avec l'API Flask sur le port **5050** :

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Statut de l'API et des DBs |
| `GET /api/task/1` | Exécuter Task 1 (Full-Text) |
| `GET /api/task/2` | Exécuter Task 2 (Accès Ciblé) |
| `GET /api/task/3` | Exécuter Task 3 (Agrégation) |
| `GET /api/data/stats` | Statistiques des données |
| `POST /api/data/generate?count=N` | Générer N logs |
| `DELETE /api/data/clear` | Vider les DBs |

## 🎨 UI/UX

- Layout full-width responsive
- Grille 4 colonnes pour le health check
- Grille 3 colonnes pour les tâches
- Thème sombre avec accents colorés
- Animations de chargement

## 📋 Scripts npm

```bash
npm run dev      # Lancer en mode développement
npm run build    # Build production
npm run lint     # Vérifier le code avec ESLint
npm run preview  # Prévisualiser le build
```
