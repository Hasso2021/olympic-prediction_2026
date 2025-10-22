# Configuration des Variables d'Environnement

## 🔐 Sécurité

Ce projet utilise des variables d'environnement pour stocker les informations sensibles comme les clés API et les mots de passe.

## 📋 Configuration requise

### 1. Créer le fichier `.env`

Créez un fichier `.env` à la racine du dossier `backend/` avec le contenu suivant :

```env
# Configuration Supabase
SUPABASE_URL=https://xecsougqsdyrrzscmtgn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhlY3NvdWdxc2R5cnJ6c2NtdGduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODE5NjksImV4cCI6MjA3NjU1Nzk2OX0.0rVlN_DPpNCnpujb4WIu_w3EFfzZFHSkolhHBjQzO6o

# Configuration du serveur
PORT=3001
NODE_ENV=development

# Base de données (optionnel)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olympic_prediction
DB_USER=postgres
DB_PASSWORD=your_password_here

# JWT Secret (pour l'authentification future)
JWT_SECRET=your_jwt_secret_here

# API Keys (si nécessaire)
API_KEY=your_api_key_here
```

### 2. Variables obligatoires

- `SUPABASE_URL` : URL de votre projet Supabase
- `SUPABASE_KEY` : Clé API de votre projet Supabase

### 3. Variables optionnelles

- `PORT` : Port du serveur (défaut: 3001)
- `NODE_ENV` : Environnement (development/production)
- `DB_*` : Configuration de base de données locale
- `JWT_SECRET` : Secret pour l'authentification JWT
- `API_KEY` : Clés API externes

## 🚀 Utilisation

### Démarrage du serveur

```bash
# Installer les dépendances
npm install

# Démarrer le serveur
npm run dev
```

### Vérification

Le serveur devrait démarrer sur le port 3001 et se connecter à Supabase.

## ⚠️ Sécurité

- **NE JAMAIS** commiter le fichier `.env`
- **NE JAMAIS** partager vos clés API
- Utilisez des variables d'environnement différentes pour chaque environnement (dev, staging, prod)

## 🔧 Dépannage

### Erreur "SUPABASE_KEY environment variable is required"

1. Vérifiez que le fichier `.env` existe
2. Vérifiez que la variable `SUPABASE_KEY` est définie
3. Redémarrez le serveur

### Erreur de connexion Supabase

1. Vérifiez que `SUPABASE_URL` est correct
2. Vérifiez que `SUPABASE_KEY` est valide
3. Vérifiez que les politiques RLS sont configurées
