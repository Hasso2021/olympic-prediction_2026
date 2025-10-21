# Backend Olympic Prediction

Ce dossier contient le backend de l'application de prédiction olympique utilisant Supabase.

## Structure

```
backend/
├── database/
│   └── supabase.js      # Configuration et connexion Supabase
├── config.js            # Configuration générale
├── index.js             # Point d'entrée du serveur
├── package.json         # Dépendances Node.js
└── README.md           # Ce fichier
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du dossier backend avec :

```env
SUPABASE_URL=https://xecsougqsdyrrzscmtgn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhlY3NvdWdxc2R5cnJ6c2NtdGduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODE5NjksImV4cCI6MjA3NjU1Nzk2OX0.0rVlN_DPpNCnpujb4WIu_w3EFfzZFHSkolhHBjQzO6o
PORT=3001
NODE_ENV=development
```

## Installation

```bash
cd backend
npm install
```

## Démarrage

### Mode développement
```bash
npm run dev
```

### Mode production
```bash
npm start
```

## API Endpoints

- `GET /` - Informations sur l'API
- `GET /api/health` - Vérification de l'état de l'API et de la connexion Supabase

## Connexion Supabase

La connexion Supabase est configurée dans `database/supabase.js` et utilise les credentials fournis. Le client Supabase est exporté et peut être utilisé dans d'autres modules.

### Utilisation

```javascript
import supabase from './database/supabase.js'

// Exemple d'utilisation
const { data, error } = await supabase
  .from('your_table')
  .select('*')
```
