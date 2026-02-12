# Plan de modularisation Mage (microservices)

## Contexte observé dans ce dépôt
- Le projet tourne actuellement en **mono-service Mage** via `docker-compose.yml` (service `magic`).【F:docker-compose.yml†L1-L10】
- Le dépôt contient déjà un **générateur d’API de prédiction** (Flask) exporté par un pipeline, ce qui peut servir de **microservice indépendant** de l’orchestrateur Mage.【F:mlops_demo/data_exporters/prediction_svc.py†L11-L141】
- La documentation interne mentionne la **modularité des blocs de pipeline**, ce qui facilite la séparation fonctionnelle par domaine (ingestion, training, scoring, monitoring).【F:README.md†L44-L45】

## Objectif
Rester sur Mage AI, **découper l’architecture** et planifier une exécution **multi-services** pour:
1. isoler l’orchestration (Mage),
2. isoler l’exécution des pipelines (workers),
3. exposer des microservices de prédiction (online),
4. séparer les dépendances et le cycle de vie de chaque composant.

## Limitation actuelle
L’accès à la documentation publique Mage AI est **bloqué par la passerelle réseau (HTTP 403)** dans cet environnement, ce qui empêche de citer la doc officielle directement.  
➡️ Ce plan est donc basé sur l’état du repo + patterns standard Mage/ETL, et doit être **validé** quand l’accès à la documentation est rétabli.

## Architecture cible (conceptuelle)
> Découper les responsabilités tout en restant sur Mage AI.

1. **Service “Mage API/UI”**
   - Rôle : UI web + API Mage + orchestration des pipelines.
   - Déduit du service `magic` actuel dans `docker-compose.yml`.【F:docker-compose.yml†L1-L10】

2. **Service “Mage Scheduler” (optionnel selon doc)**
   - Rôle : planification des exécutions (cron, triggers).
   - Si Mage expose un mode “scheduler” ou “server + scheduler”, on sépare ce rôle.

3. **Service “Mage Worker(s)”**
   - Rôle : exécuter les blocs de pipeline.
   - Possibilité d’avoir plusieurs workers pour scaler horizontalement.

4. **Service “Prediction API (online)”**
   - Rôle : microservice de scoring HTTP dédié.
   - Se base sur le générateur de service `prediction_svc.py`, qui produit `app.py` et `requirements.txt` dans `mlops_demo/prediction_service`.【F:mlops_demo/data_exporters/prediction_svc.py†L11-L141】

5. **Services d’infrastructure**
   - Base de données (Postgres) pour metadata + state.
   - Cache/queue (Redis ou autre) si requis par Mage.
   - Stockage modèles/artifacts (volume partagé ou object storage).

## Plan d’exécution (étapes)
1. **Documenter le runtime Mage**
   - Vérifier dans la doc Mage : modes de démarrage (server, scheduler, worker), variables d’environnement, stockage, DB, queue.
   - Livrable : un tableau des services à séparer + leurs commandes exactes.

2. **Refactor du `docker-compose.yml`**
   - Remplacer le service monolithique par :
     - `mage-server` (UI/API),
     - `mage-scheduler` (si disponible),
     - `mage-worker` (réplicable),
     - `prediction-service`.
   - Conserver volumes et configs partagées (`/home/src` ou équivalent).

3. **Extraction du microservice de prédiction**
   - Utiliser le pipeline `prediction_svc.py` pour générer `mlops_demo/prediction_service`.
   - Créer un Dockerfile dédié pour `prediction_service`.
   - Déployer comme service indépendant (ports propres, healthcheck).

4. **Séparation des environnements**
   - Définir des `ENV` différents par service (prod/dev).
   - Isoler les dépendances Python entre Mage et `prediction-service`.

5. **Observabilité**
   - Ajouter logs centralisés et métriques par service.
   - Vérifier les healthchecks pour UI, scheduler, workers, API prediction.

## Prochaines actions recommandées
- **Réessayer l’accès doc Mage** (ou fournir un accès local) pour valider:
  - les commandes exactes de split server/scheduler/worker,
  - les variables d’environnement officielles,
  - l’architecture recommandée en production.
- Une fois validé, préparer un **docker-compose multi-services** + scripts de démarrage.
