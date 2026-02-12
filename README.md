# A propos de Mage

Mage AI est une plateforme moderne de data engineering, conçue pour faciliter la création, le déploiement et la gestion de pipelines de données grâce à l'intelligence artificielle. Elle s'adresse aux équipes de données qui souhaitent automatiser, collaborer et accélérer la transformation et l'analyse de leurs données, tout en bénéficiant d'une interface intuitive et d'outils puissants.

Mage AI vise à rendre l'ingénierie des données plus accessible, collaborative et automatisée, tout en offrant la puissance nécessaire pour répondre aux besoins des entreprises modernes.

## Fonctionnalités principales de Mage AI

**1. Création intuitive de pipelines**
Mage AI propose un éditeur interactif, de type notebook, permettant de construire des pipelines en Python, SQL ou R. On peut assembler des blocs de code réutilisables, visualiser immédiatement les résultats et organiser les dépendances entre chaque étape du pipeline.

**2. Orchestration et automatisation**
Les pipelines peuvent être déclenchés selon un planning, en réponse à un évènement ou via une requête API. Mage gère l'automatisation, le monitoring et l'orchestration de milliers de pipelines sans complexité supplémentaire.

**3. Intégration et transformation de données**
Mage AI synchronise et extrait des données depuis de nombreuses sources tierces, puis les transforme en temps réel ou en mode batch, avant de les charger dans un data warehouse ou un data lake. Les connecteurs intégrés facilitent cette intégration.

**4. Monitoring et observabilité**
La plateforme offre des outils pour surveiller l'exécution des pipelines, générer des alertes en temps réel, visualiser les flux de données et assurer la qualité des données grâce à des tests intégrés.

**5. Collaboration et gestion des utilisateurs**
Mage AI permet à plusieurs utilisateurs de collaborer sur des projets, avec un contrôle fin des accès, des environnements de développement isolés et un suivi des versions via Git.

**6. Scalabilité et performance**
L'architecture de Mage AI est pensée pour le passage à l'échelle : elle peut traiter de gros volumes de données, exécuter des pipelines massivement parallèles et s'intégrer à des outils comme Spark.

**7. Sécurité et conformité**
La plateforme intègre la gestion des secrets, l'authentification avancée, le contrôle d'accès par rôles et des options de déploiement flexibles (cloud, hybride, on-premise).

### Illustration ASCII : Structure d'un pipeline Mage AI

Voici une représentation simplifiée d'un pipeline Mage AI :

```sh
+------------------+      +------------------+      +------------------+
|  Extraction      | ---> | Transformation   | ---> |  Chargement      |
| (Sources externes)|     | (Python/SQL/R)   |     | (Data warehouse) |
+------------------+      +------------------+      +------------------+
        |                        |                          |
   [Blocs de code]         [Blocs de code]             [Blocs de code]
```

Chaque étape du pipeline est composée de blocs indépendants, testables et réutilisables, ce qui favorise la modularité et la maintenabilité des workflows.


# MLOps Masterclass - Quick Start Guide

## For the Masterclass Presentation

### 1-Minute Setup
```bash
cd /home/seb/project/mage-ai-demo
make setup      # Builds images with pinned version 0.9.79 and starts all services
```

### 5-Minute Demo
```bash
make demo       # Runs complete workflow demo:
                # ✅ Service health checks
                # ✅ Model registry display
                # ✅ Prediction test
                # ✅ Pipeline listing
```

### 15-Minute Feature Showcase
```bash
# Show pipelines
make list-pipelines

# Show model versions
make show-models
make show-latest-model

# Test prediction API
make test-predict

# Check logs
make logs-scheduler
```

### Live UI Demo
```bash
# Open in browser
http://localhost:6789

# Features to show:
# 1. Pipeline structure in left panel
# 2. Block execution in main area
# 3. Data preview at each step
# 4. Run history and logs
# 5. Trigger configuration
```


## Key Makefile Commands for Presentation

| Command | Duration | Use Case |
|---------|----------|----------|
| `make setup` | 60s | Initialize everything |
| `make demo` | 30s | Quick complete demo |
| `make health` | 10s | Show service status |
| `make list-pipelines` | 5s | Show available pipelines |
| `make show-models` | 5s | Display model registry |
| `make test-predict` | 5s | Test prediction API |
| `make logs-web` | instant | Debug web server |
| `make logs-scheduler` | instant | Debug scheduler |


## Talking Points

### "What Makes Mage Special?"

1. **Interactive Development** (Demo: Open UI → Show notebook interface)
   - Code in modular blocks
   - Preview data at each step
   - Test independently

2. **Built-in Orchestration** (Demo: make list-pipelines → make run-pipeline)
   - No need for Airflow/Prefect
   - Native scheduling
   - Distributed execution

3. **Model Versioning** (Demo: make show-models → make show-latest-model)
   - Automatic model tracking
   - Version registry
   - A/B testing support

4. **Production Ready** (Show ARCHITECTURE.md)
   - Microservices architecture
   - Horizontal scaling
   - Cloud executor support

5. **Low Learning Curve** (Demo: make help)
   - Single command deployment
   - Familiar Python syntax
   - Clear documentation


## Common Q&A Responses

**Q: How do I scale this?**
```bash
# Look at ARCHITECTURE.md for:
# - Multi-instance web servers (behind load balancer)
# - Multi-instance schedulers (Redis coordination)
# - Cloud executors (ECS/Kubernetes/GCP)
```

**Q: Can I use my own data?**
```bash
# Yes! Show mlops_demo/pipelines/
# Create new pipelines in the UI
# Mount custom data volumes in docker-compose.yml
```

**Q: How is this different from Airflow?**
```bash
# Reference: MASTERCLASS.md comparison table
# Key differences:
# - Lower learning curve
# - Interactive IDE
# - Modular code blocks
# - Built-in data preview
```

**Q: What about monitoring?**
```bash
# Show: make logs-* commands
# Also: Built-in run history in UI
# Explain: Easy integration with external tools
```


## Potential presentation Timeline (45 min)

| Time | Activity | Command |
|------|----------|---------|
| 0:00 | Intro | Read MASTERCLASS.md title |
| 2:00 | Problem Statement | Show fragmented stack diagram |
| 5:00 | Solution | Show Mage unified stack diagram |
| 7:00 | Architecture | `make info && make health` |
| 12:00 | Live Demo | `make setup` (if not done) |
| 15:00 | Features | `make list-pipelines` |
| 20:00 | Model Registry | `make show-models` |
| 25:00 | Predictions | `make test-predict` |
| 30:00 | Comparison | Show MASTERCLASS.md table |
| 35:00 | Use Cases | Discuss scenarios |
| 40:00 | Questions | `make logs-*` for debugging |
| 45:00 | Wrap Up | Summary slide |


## Troubleshooting During Demo

| Issue | Solution |
|-------|----------|
| Services not starting | `make down && make setup` |
| Port 6789 already in use | `make down && lsof -i :6789 && kill <PID>` |
| Slow startup | Check `make logs` for initialization |
| Prediction API not responding | `make predict-health` |
| Can't see logs | `make logs-web` or `make logs-scheduler` |


## Files to Reference During Presentation

1. **`docs/MASTERCLASS.md`** - Complete guide (14 KB)
   - Open for comparisons
   - Reference for architecture details

2. **`docs/ARCHITECTURE.md`** - Technical deep-dive (12 KB)
   - Show for scaling options
   - Reference for microservices

3. **Makefile** - Available commands (500 lines)
   - Show with `make help`
   - Demonstrate individual commands


## Key Takeaways to Emphasize

✅ **Reproducibility** - Pinned version 0.9.79 (no surprises)
✅ **Simplicity** - Single `make demo` for complete workflow
✅ **Production-Ready** - Microservices architecture at day 1
✅ **Complete Solution** - No need for separate tools
✅ **Open Source** - No vendor lock-in


## After the Masterclass

Attendees can:
1. Clone this repository
2. Run `make setup` in their environment
3. Experiment with the example pipelines
4. Create custom pipelines in the UI
5. Modify Makefile for their use cases


## Demo Commands

```sh
# Make a prediction
make high-risk
# Output: Run ID: 13

# Show the prediction result
make show-result ID=13

# Or show the latest result
make latest-result

# Or make prediction and show result immediately
make predict-show

# See all available data files
make list-files

# Clean formatted display
make clean-result ID=12
```


**Pro Tips:**
- Keep terminal window large for easy reading
- Have MASTERCLASS.md open for reference
- Use `make health` frequently to show stability
- Show logs when something happens
- Mention all commands available with `make help`

**Good Luck! 🎓**
