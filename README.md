# Mage AI Microservices MLOps Demo

Ce dépôt présente une démo MLOps complète avec Mage AI, incluant le rechargement dynamique des modèles, le versioning des données et la traçabilité (lineage) de bout en bout, le tout dans une architecture microservices.

> **Version Mage AI :** 0.9.79 (pinned pour la reproductibilité)

## Architecture (vue d’ensemble)

```
┌─────────────────────────────────────────────────────────────┐
│                    Utilisateurs externes                    │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP (6789)
                     ▼
            ┌────────────────────┐
            │   Mage Web Server  │
            │ (web_server role)  │
            │  UI + API          │
            └────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    PostgreSQL     Redis      Code Files
   (metadata)  (coordination) (volumes)
        ▲            ▲            ▲
        │            │            │
        └────────────┼────────────┘
                     │
            ┌────────▼───────────┐
            │  Mage Scheduler    │
            │ (scheduler role)   │
            └────────────────────┘
                     │
        Enqueued     ▼ (in-memory queue)
        Runs     ┌─────────────────┐
                 │ Executor Pool   │
                 │ (20 threads)    │
                 └─────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   Datasets              Prediction API
                        (Flask, port 5000)
                          - /predict
                          - /health
                          - /lineage
```

Pour les détails techniques et les stratégies de scalabilité, voir `docs/ARCHITECTURE.md`.

## Commandes essentielles (Makefile)

| Commande | Usage |
|---------|------|
| `make setup` | Build des images et démarrage des services |
| `make demo` | Démo complète (health, registry, predict, pipelines) |
| `make health` | Vérifier l’état des services |
| `make list-pipelines` | Lister les pipelines disponibles |
| `make show-models` | Afficher les versions de modèles |
| `make show-latest-model` | Afficher le dernier modèle déployé |
| `make test-predict` | Lancer une prédiction de test |
| `make logs-web` | Logs du serveur web |
| `make logs-scheduler` | Logs du scheduler |
| `make down` | Arrêter tous les services |

## API de prédiction et lineage

Exemples d’appels rapides :

```bash
# Prédiction (rechargement dynamique du modèle)
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"account_age": 24, "monthly_charges": 65.5, "total_charges": 1569.5, "num_services": 3, "customer_service_calls": 4, "contract_length": 12, "payment_method_score": 0.8, "usage_frequency": 0.7, "support_tickets": 2, "satisfaction_score": 0.6}'

# Health check
curl http://localhost:5000/health | jq .

# Lineage complet
curl http://localhost:5000/lineage | jq .
```

## Démarrer et exécuter un pipeline dans l’UI Mage

1. Ouvrir l’UI : `http://localhost:6789`
2. Dans le panneau de gauche, ouvrir **Pipelines** → **demo_mlops**
3. Vérifier les blocs (make_dataset → preprocessing → training → registry → deployment)
4. Cliquer sur **Run** (en haut à droite) pour lancer le pipeline
5. Suivre les logs et la progression dans le panneau d’exécution

## Points clés MLOps

- **Dynamic Model Reload** : le service de prédiction recharge le dernier modèle à chaque requête
- **Data Versioning** : version des datasets via SHA256 + ID timestampé
- **Lineage complet** : données, code, métriques, hyperparamètres et historique des prédictions

## Documentation utile

- `docs/MASTERCLASS.md` — présentation complète des fonctionnalités et comparatifs
- `docs/ARCHITECTURE.md` — architecture microservices et scalabilité
- `Makefile` — commandes de démo et d’exploitation

## Pré-requis

- Docker
- Docker Compose
- Make

## Dépannage rapide

- **Services ne démarrent pas** : `make down && make setup`
- **Port 6789 déjà utilisé** : `make down` puis libérer le port
- **Prediction API en 404** : vérifier `mlops_demo/model_registry/latest.json`
- **Scheduler inactif** : vérifier Redis et la variable `REDIS_URL`
