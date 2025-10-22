# Database Module

Ce dossier contient tous les fichiers liés à la base de données pour l'application Olympic Prediction.

## Structure

```
database/
├── index.js           # Point d'entrée principal
├── config.js          # Configuration Supabase et serveur
├── supabase.js        # Connexion et client Supabase
├── olympic-tables.js  # Fonctions pour les tables olympiques
├── seed-hosts.js      # Données de test pour la table hosts
└── README.md          # Ce fichier
```

## Connexion à la base de données

### Configuration Supabase
- **URL** : `https://xecsougqsdyrrzscmtgn.supabase.co`
- **Clé API** : Configurée dans `config.js`
- **Client** : Exporté depuis `supabase.js`

### Fichiers de connexion

#### `config.js`
Contient la configuration Supabase et du serveur :
```javascript
export const supabaseConfig = {
  url: 'https://xecsougqsdyrrzscmtgn.supabase.co',
  key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
}
```

#### `supabase.js`
Gère la connexion Supabase :
- Création du client Supabase
- Test de connexion
- Export du client pour utilisation dans d'autres modules

## Tables disponibles

### Table `athlete`
- Fonctions : `getAthletes()`, `getAthletesByCountry()`, `getAthletesBySport()`

### Table `hosts`
- Fonctions : `getHosts()`, `getHostsByYear()`, `getHostsByCountry()`
- Données de test : `seedHostsData()`, `checkHostsData()`

## Utilisation

### Import simple
```javascript
import { testConnection, olympicTables, serverConfig } from './database/index.js'
```

### Import spécifique
```javascript
import { testConnection } from './database/supabase.js'
import { olympicTables } from './database/olympic-tables.js'
```

## Test de connexion

```javascript
import { testConnection } from './database/index.js'

const isConnected = await testConnection()
if (isConnected) {
  console.log('✅ Connexion Supabase réussie!')
}
```

## Variables d'environnement

Créez un fichier `.env` à la racine du backend :

```env
SUPABASE_URL=https://xecsougqsdyrrzscmtgn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
PORT=3001
NODE_ENV=development
```
