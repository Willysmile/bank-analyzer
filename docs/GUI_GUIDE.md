# Guide d'Utilisation de l'Interface Graphique

## Lancer la GUI

```bash
python gui.py
```

## Onglets Disponibles

### 1️⃣ Import (📥)

**Objectif** : Importer un fichier CSV depuis ta banque

**Étapes** :
1. Clique sur "Parcourir..." pour sélectionner ton fichier CSV
2. Le nom du fichier s'affiche
3. Clique sur "📥 Importer"
4. Attends la fin du traitement
5. Consulte les résultats dans la zone de texte

**Informations affichées** :
- ✅ Nombre de transactions importées
- ⚠️ Nombre d'avertissements (doublons, erreurs de parsing)
- 📝 Détail des avertissements

**Formats supportés** :
- Encodage : UTF-8 ou ISO-8859-1 (auto-détecté)
- Séparateur : Virgule
- Colonnes attendues : Date, Libellé, Débit euros, Crédit euros

---

### 2️⃣ Transactions (📋)

**Objectif** : Consulter toutes tes transactions

**Filtres disponibles** :
- **Afficher** : Nombre de transactions à afficher (10 à 500)

**Colonnes** :
- **Date** : Date de la transaction (JJ/MM/AAAA)
- **Description** : Libellé complet de la transaction
- **Montant** : Montant en euros
  - 🟢 Vert = Revenu (crédit)
  - 🔴 Rouge = Dépense (débit)
- **Catégorie** : Catégorie attribuée (ou "-" si non catégorisée)
- **Type** : Type de transaction (PAIEMENT, PRELEVEMENT, VIREMENT)

**Actions** :
- Clique sur "🔄 Actualiser" pour recharger la liste
- Double-clic sur une transaction pour voir les détails
- Clic-droit pour accéder au menu contextuel :
  - 🏷️ **Catégoriser** : Changer la catégorie
  - 🔄 **Marquer récurrent** : Transaction mensuelle
  - ⭐ **Marquer vital** : Dépense essentielle
  - 💰 **Provenant d'épargne** : Transaction d'épargne

---

### 3️⃣ Catégorisation (🏷️)

**Objectif** : Catégoriser automatiquement tes transactions

**Information** :
- Affiche le nombre de transactions **non catégorisées**

**Actions disponibles** :
- **🤖 Catégoriser Automatiquement** : Lance la catégorisation auto sur toutes les transactions non catégorisées
- **🔄 Actualiser** : Recharge le nombre de transactions restantes

**Règles de catégorisation** :
La GUI affiche les règles utilisées pour la catégorisation automatique. Chaque catégorie a des mots-clés associés :

```
🏷️ Alimentation:
   Mots-clés: lidl, carrefour, intermarche, restaurant, mc donald, pizza

🏷️ Transport:
   Mots-clés: essence, parking, sncf, bus, metro, uber, taxi

🏷️ Logement:
   Mots-clés: loyer, immobilier, proprio, syndic

🏷️ Internet/Téléphone:
   Mots-clés: edf, orange, water, eau, electricite, gaz

🏷️ Loisirs:
   Mots-clés: cinema, theatre, spotify, netflix, jeux

🏷️ Santé:
   Mots-clés: pharmacie, docteur, medical, sante, dentiste

🏷️ Éducation:
   Mots-clés: ecole, universite, formation, cours
```

Si un mot-clé apparaît dans la description de la transaction, elle sera catégorisée automatiquement.

---

### 4️⃣ Rapports (📊)

**Objectif** : Générer des rapports détaillés avec statistiques

**Filtres disponibles** :

1. **Période** :
   - **Du** : Date de début (format: YYYY-MM-DD)
   - **Au** : Date de fin (format: YYYY-MM-DD)
   - Laisse vide pour inclure toutes les dates

2. **Catégorie** :
   - Sélectionne "Toutes" pour un rapport global
   - Ou une catégorie spécifique (Alimentation, Transport, etc.)

**Action** :
- Clique sur "📊 Générer" pour générer le rapport

**Statistiques affichées** :

```
📊 RAPPORT FINANCIER
================================================

Période: [date début] à [date fin]
Catégorie: [catégorie ou rien]

================================================
📊 Statistiques Générales
================================================
Nombre de transactions: X
Revenu total: €X.XX
Dépenses totales: €X.XX
Bilan net: €X.XX
Moyenne par transaction: €X.XX
Plus grand revenu: €X.XX
Plus grande dépense: €X.XX

================================================
📈 Par Catégorie
================================================
Alimentation: €X.XX
Transport: €X.XX
Logement: €X.XX
...
```

---

### 5️⃣ Budget (💰)

**Objectif** : Définir et suivre tes objectifs budgétaires

**Fonctionnalités** :
- **Ajouter un objectif** : Définit un plafond de dépense pour une catégorie
- **Voir les objectifs** : Liste tous les objectifs actifs avec progression
- **Modifier/Supprimer** : Clic-droit sur un objectif pour le modifier

**Colonnes** :
- **Catégorie** : Nom de la catégorie budgétée
- **Plafond** : Montant maximum autorisé
- **Dépensé** : Montant déjà dépensé ce mois
- **Restant** : Montant restant disponible
- **Progression** : Barre de progression visuelle

---

### 6️⃣ Statistiques (📈)

**Objectif** : Analyses avancées et graphiques détaillés

**Graphiques disponibles** :
1. **Revenus vs Dépenses** : Camembert comparant revenus et dépenses
2. **Dépenses récurrentes** : Répartition charges fixes vs variables
3. **Dépenses vitales** : Analyse essentiel vs superflu
4. **Top 10 catégories** : Les 10 catégories les plus dépensées

**Métriques calculées** :
- **Tendance mensuelle** : Évolution des dépenses sur 12 mois
- **Moyennes mobiles** : Lissage des variations
- **Ratios d'épargne** : Part des revenus épargnés

---

### 7️⃣ Prévisions (🔮)

**Objectif** : Prévoir tes finances futures

**Fonctionnalités** :
- **Projection sur 6 mois** : Estimation basée sur l'historique
- **Alertes de dépassement** : Notification si tendance négative
- **Scénarios** : Simulation d'économies ou de dépenses supplémentaires

**Données affichées** :
- **Solde projeté** : Évolution du solde sur 6 mois
- **Dépenses estimées** : Prévision par catégorie
- **Risques identifiés** : Alertes sur tendances préoccupantes

---

### 8️⃣ Paramètres (⚙️)

**Objectif** : Configurer l'application et gérer les données

**Sections disponibles** :

1. **Statistiques de base** :
   - Nombre total de transactions
   - Période couverte
   - Catégories utilisées

2. **Actions de maintenance** :
   - **Supprimer les doublons** : Nettoie les transactions dupliquées
   - **Vider la base** : Supprime toutes les données (⚠️ irréversible)
   - **Exporter les données** : Sauvegarde en CSV

3. **Configuration** :
   - **Thème** : Mode sombre/clair (futur)
   - **Format d'export** : Options d'export (futur)
   - **Notifications** : Paramètres d'alertes (futur)

---

### 4️⃣ Rapports (📊)

**Objectif** : Générer des rapports détaillés avec statistiques

**Filtres disponibles** :

1. **Période** :
   - **Du** : Date de début (format: YYYY-MM-DD)
   - **Au** : Date de fin (format: YYYY-MM-DD)
   - Laisse vide pour inclure toutes les dates

2. **Catégorie** :
   - Sélectionne "Toutes" pour un rapport global
   - Ou une catégorie spécifique (Alimentation, Transport, etc.)

**Action** :
- Clique sur "📊 Générer" pour générer le rapport

**Statistiques affichées** :

```
📊 RAPPORT FINANCIER
================================================

Période: [date début] à [date fin]
Catégorie: [catégorie ou rien]

================================================
📊 Statistiques Générales
================================================
Nombre de transactions: X
Revenu total: €X.XX
Dépenses totales: €X.XX
Bilan net: €X.XX
Moyenne par transaction: €X.XX
Plus grand revenu: €X.XX
Plus grande dépense: €X.XX

================================================
📈 Par Catégorie
================================================
Alimentation: €X.XX
Transport: €X.XX
...
```

---

## Flux de Travail Recommandé

1. **Importe** tes relevés (onglet Import)
2. **Catégorise** automatiquement (onglet Catégorisation)
3. **Consulte** tes transactions (onglet Transactions)
4. **Génère** des rapports (onglet Rapports)

---

## Conseils d'Utilisation

### 💡 Bien importer

- Assure-toi que le fichier CSV est au bon format
- Les doublons ne seront pas importés deux fois
- Consulte les avertissements après chaque import

### 💡 Améliorer la catégorisation

- Ajoute tes propres mots-clés aux règles
- Catégorise manuellement les transactions mal détectées
- Réutilise les catégorisations antérieures

### 💡 Générer des rapports utiles

- Utilise des périodes cohérentes (mois, trimestre, année)
- Compare les périodes pour identifier les tendances
- Analyse par catégorie pour maîtriser tes dépenses

---

## Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+Q` | Quitter l'application |
| `Tab` | Passer à l'onglet suivant |
| `Shift+Tab` | Aller à l'onglet précédent |

---

## Dépannage

### L'application ne démarre pas

```bash
# Vérifie que Tkinter est installé
python -m tkinter
```

Si rien ne s'affiche, installe Tkinter :
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk

# Windows
# Tkinter est fourni avec Python
```

### Aucune transaction n'apparaît

1. Vérifie que tu as bien importé des fichiers
2. Clique sur "🔄 Actualiser" pour recharger
3. Augmente le nombre de transactions affichées

### La catégorisation ne fonctionne pas

- Assure-toi qu'il y a des transactions non catégorisées
- Vérifie que les mots-clés correspondent aux descriptions
- Consulte les règles affichées dans l'onglet Catégorisation

### Les rapports affichent des erreurs de date

- Utilise le format YYYY-MM-DD (ex: 2025-10-24)
- Assure-toi que la date de début ≤ date de fin

---

## Contact et Support

Pour toute question ou bug, consulte le README principal ou les issues du projet.
